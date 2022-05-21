# Simple Mercari - Build@Mercari Training Program 2022

This is a simple mercari web application.

<img width="756" alt="demo" src="https://user-images.githubusercontent.com/59286368/169643908-e40ae1a6-07cb-4394-a466-e3c6ee9ccf79.png">

### :bulb: Features
- List item
- Show items
- Display item images
- Get item by id (API only)
- Search items by keyword in name (API only)
- Delete item (API only)

### :warning: Data Validation
Data validation is implemented on both client and server side.  
Below are the constraints:  
- Item name must be no longer than 32 characters  
- Category name must be no longer than 12 characters  
- Image must be in jpg or jpeg format  

## :whale: System requirement

- docker version 20.10.14 or above
- docker-compose version 1.29.2 or above

## :beginner: How to use

1. Clone this repository and change directory to this project
   ```
   git clone https://github.com/tsoibet/mercari-build-training-2022.git && cd mercari-build-training-2022
   ```
2. Run docker compose
   ```
   docker-compose up
   ```
3. Visit http://localhost:3000


## :iphone: Reponsive web design :desktop_computer:

Examples:

| iPhone XR (414x896) | iPad mini (768x1024) | Desktop (1333x1000) |
| :---: | :---: | :---: |
| <img height="300" alt="iPhone" src="https://user-images.githubusercontent.com/59286368/169643854-c589faa3-0170-4018-81ab-9d8ce2c26219.png"> | <img height="300" alt="iPad" src="https://user-images.githubusercontent.com/59286368/169643860-a5a65b20-858f-44e1-a91b-a0051a3a224f.png"> | <img height="300" alt="Desktop" src="https://user-images.githubusercontent.com/59286368/169643864-668bb834-775e-44ee-be55-3af7147b11f0.png"> |

<br/>

#### Remarks 

:pushpin: *As python was used to write the backend API, the `go` directory is not used.*  
:pushpin: *Branches are remained in the repository for record of progress. Earlier steps are labelled with git tags.*  

<br/>

### :arrow_down: Below is the official README of Build@Mercari Training Program. :arrow_down:

-----


This is @tsoibet's build training repository.

Build trainingの前半では個人で課題に取り組んでもらい、Web開発の基礎知識をつけていただきます。
ドキュメントには詳細なやり方は記載しません。自身で検索したり、リファレンスを確認したり、チームメイトと協力して各課題をクリアしましょう。

ドキュメントには以下のような記載があるので、課題を進める際に参考にしてください。

In the first half of Build@Mercari program, you will work on individual tasks to understand the basics of web development. Detailed instructions are not given in each step of the program, and you are encouraged to use official documents and external resources, as well as discussing tasks with your teammates and mentors.

The following icons indicate pointers for 

**:book: Reference**

* そのセクションを理解するために参考になるUdemyやサイトのリンクです。課題内容がわからないときにはまずReferenceを確認しましょう。
* Useful links for Udemy courses and external resources. First check those references if you're feeling stuck.

**:beginner: Point**

* そのセクションを理解しているかを確認するための問いです。 次のステップに行く前に、**Point**の問いに答えられるかどうか確認しましょう。
* Basic questions to understand each section. Check if you understand those **Points** before moving on to the next step.

## Tasks

- [x] **STEP1** Git ([JA](document/step1.ja.md)/[EN](document/step1.en.md))
- [x] **STEP2** Setup environment ([JA](document/step2.ja.md)
  /[EN](document/step2.en.md))
- [x] **STEP3** Develop API ([JA](document/step3.ja.md)
  /[EN](document/step3.en.md))
- [x] **STEP4** Docker ([JA](document/step4.ja.md)/[EN](document/step4.en.md))
- [x] **STEP5** (Stretch) Frontend ([JA](document/step5.ja.md)
  /[EN](document/step5.en.md))
- [x] **STEP6** (Stretch)  Run on docker-compose ([JA](document/step6.ja.md)
  /[EN](document/step6.en.md))

### Other documents

- 効率的に開発できるようになるためのTips / Tips for efficient development ([JA](document/tips.ja.md)/[EN](document/tips.en.md))
