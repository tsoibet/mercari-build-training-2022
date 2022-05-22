package main

import (
    "crypto/sha256"
    "database/sql"
    "fmt"
    "io"
    "net/http"
    "os"
    "path"
    "strings"

    "github.com/labstack/echo/v4"
    "github.com/labstack/echo/v4/middleware"
    "github.com/labstack/gommon/log"

    _ "github.com/mattn/go-sqlite3"
)

const (
    ImgDir        = "image"
    DATABASE_NAME = "../db/mercari.sqlite3"
    SCHEMA_NAME   = "../db/items.db"
)

var db *sql.DB

type Response struct {
    Message string `json:"message"`
}

type Items struct {
    Items []Item `json:"items"`
}

type Item struct {
    Id            int    `json:"id"`
    Name          string `json:"name"`
    Category      string `json:"category"`
    ImageFileName string `json:"image_filename"`
}

func root(c echo.Context) error {
    res := Response{Message: "Hello, world!"}
    return c.JSON(http.StatusOK, res)
}

func addItem(c echo.Context) error {
	c.Logger().Infof("Received add_item request.")
	// Get form data
    name := c.FormValue("name")
    category := c.FormValue("category")
    image, err := c.FormFile("image")
    if err != nil {
        return c.JSON(http.StatusInternalServerError, err)
    }
    imageBinary, err := image.Open()
    if err != nil {
        return c.JSON(http.StatusInternalServerError, err)
    }
    defer imageBinary.Close()
    var imageByte []byte
    _, err = imageBinary.Read(imageByte)
    if err != nil {
        return c.JSON(http.StatusInternalServerError, err)
    }
    newImageName := fmt.Sprintf("%x%s", sha256.Sum256(imageByte), ".jpg")

    imagePath := path.Join(ImgDir, newImageName)
    dst, err := os.Create(imagePath)
    if err != nil {
        return c.JSON(http.StatusInternalServerError, err)
    }
    defer dst.Close()

    if _, err = io.Copy(dst, imageBinary); err != nil {
        return c.JSON(http.StatusInternalServerError, err)
    }
    var categoryId int
    row := db.QueryRow(`SELECT id FROM category WHERE name = ?`, category)
    if err := row.Scan(&categoryId); err == sql.ErrNoRows {
        res, err := db.Exec(`INSERT INTO category(name) VALUES (?)`, category)
        if err != nil {
            c.Logger().Infof("Failed to add category.")
            return c.JSON(http.StatusInternalServerError, err)
        }
        id, err := res.LastInsertId()
        if err != nil {
            c.Logger().Infof("Failed to get last inserted category id.")
            return c.JSON(http.StatusInternalServerError, err)
        }
        categoryId = int(id)
    }

    _, err = db.Exec(`INSERT INTO items(name, category_id, image_filename) VALUES (?, ?, ?)`, name, categoryId, newImageName)
    if err != nil {
        return c.JSON(http.StatusInternalServerError, err)
    }
    c.Logger().Infof("Item %s of %s category is added into database.", name, category)

    message := fmt.Sprintf("Item %s of %s category is received.", name, category)
    res := Response{Message: message}

    return c.JSON(http.StatusOK, res)
}

func getItems(c echo.Context) error {
    c.Logger().Infof("Received get_items request.")
    rows, err := db.Query(`
	SELECT items.id, items.name, category.name as category, items.image_filename 
	FROM items INNER JOIN category 
	ON category.id = items.category_id `)
    if err != nil {
        return c.JSON(http.StatusInternalServerError, err)
    }
    defer rows.Close()

    data := []Item{}
    for rows.Next() {
        item := Item{}
        err = rows.Scan(&item.Id, &item.Name, &item.Category, &item.ImageFileName)
        if err != nil {
            return c.JSON(http.StatusInternalServerError, err)
        }
        data = append(data, item)
    }
    res := Items{Items: data}
	c.Logger().Infof("Returning all items.")
    return c.JSON(http.StatusOK, res)
}

func getItem(c echo.Context) error {
	id := c.Param("item_id")
	c.Logger().Infof("Received get_item request of item id: %s", id)
	row:= db.QueryRow(`
	SELECT items.id, items.name, category.name as category, items.image_filename
	FROM items INNER JOIN category
	ON category.id = items.category_id
	WHERE items.id = (?)`, id)

	item := Item{}
	if err := row.Scan(&item.Id, &item.Name, &item.Category, &item.ImageFileName); err == sql.ErrNoRows {
		c.Logger().Infof("Failed to get item: Item not found")
		return c.JSON(http.StatusNotFound, nil)
	}
	c.Logger().Infof("Returning the item of id: %s", id)
	return c.JSON(http.StatusOK, item)
}

func searchItem(c echo.Context) error {
    keyword := c.QueryParam("keyword")
    c.Logger().Infof("Received search_item request of search keyword: %s", keyword)
    rows, err := db.Query(`
	SELECT items.id, items.name, category.name as category, items.image_filename 
	FROM items INNER JOIN category 
	ON category.id = items.category_id 
	WHERE items.name LIKE (?)`, "%"+keyword+"%")
    if err != nil {
        return c.JSON(http.StatusInternalServerError, err)
    }
    defer rows.Close()

    data := []Item{}
    for rows.Next() {
        item := Item{}
        err = rows.Scan(&item.Id, &item.Name, &item.Category, &item.ImageFileName)
        if err != nil {
            return c.JSON(http.StatusInternalServerError, err)
        }
        data = append(data, item)
    }
    res := Items{Items: data}
	c.Logger().Infof("Returning items with name containing: %s", keyword)
    return c.JSON(http.StatusOK, res)
}

func getImg(c echo.Context) error {
    // Create image path
    imgPath := path.Join(ImgDir, c.Param("imageFilename"))

    if !strings.HasSuffix(imgPath, ".jpg") {
        res := Response{Message: "Image path does not end with .jpg"}
        return c.JSON(http.StatusBadRequest, res)
    }
    if _, err := os.Stat(imgPath); err != nil {
        c.Logger().Infof("Image not found: %s", imgPath)
        imgPath = path.Join(ImgDir, "default.jpg")
    }
    return c.File(imgPath)
}

func main() {
    e := echo.New()

    // Middleware
    e.Use(middleware.Logger())
    e.Use(middleware.Recover())
    e.Logger.SetLevel(log.INFO)

    var err error
    db, err = sql.Open("sqlite3", DATABASE_NAME)
    if err != nil {
        e.Logger.Panicf("Failed to connect to database.")
        return
    }
    defer db.Close()

    front_url := os.Getenv("FRONT_URL")
    if front_url == "" {
        front_url = "http://localhost:3000"
    }
    e.Use(middleware.CORSWithConfig(middleware.CORSConfig{
        AllowOrigins: []string{front_url},
        AllowMethods: []string{http.MethodGet, http.MethodPut, http.MethodPost, http.MethodDelete},
    }))

    // Routes
    e.GET("/", root)
    e.GET("/items", getItems)
    e.GET("/items/:item_id", getItem)
    e.GET("/search", searchItem)
    e.POST("/items", addItem)
    e.GET("/image/:imageFilename", getImg)

    // Start server
    e.Logger.Fatal(e.Start(":9000"))
}
