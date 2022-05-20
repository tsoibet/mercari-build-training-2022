import React, { useState } from 'react';

const server = process.env.API_URL || 'http://127.0.0.1:9000';

interface Prop {
  onListingCompleted?: () => void;
}

type formDataType = {
  name: string,
  category: string,
  image: string | File,
}

export const Listing: React.FC<Prop> = (props) => {
  const { onListingCompleted } = props;
  const initialState = {
    name: "",
    category: "",
    image: "",
  };
  const [values, setValues] = useState<formDataType>(initialState);

  const onChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setValues({ ...values, [event.target.name]: event.target.value });
  };
  const onImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setValues({ ...values, [event.target.name]: event.target.files![0] });
  };

  const onSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const data = new FormData()
    data.append('name', values.name)
    data.append('category', values.category)
    data.append('image', values.image)

    fetch(server.concat('/items'), {
      method: 'POST',
      mode: 'cors',
      body: data,
    })
      .then(response => response.json())
      .then(data => {
        console.log('POST success:', data);
        onListingCompleted && onListingCompleted();
      })
      .catch((error) => {
        console.error('POST error:', error);
      })
  };
  return (
    <div className='Listing'>
      <form autoComplete='off' onSubmit={onSubmit}>
        <div className='InputBox'>
          <input type='text' name='name' id='name' placeholder='name' maxLength={30} onChange={onChange} required />
          <input type='text' name='category' id='category' placeholder='category' maxLength={12} onChange={onChange} required/>
          <input type='file' name='image' id='image' accept='.jpg' onChange={onImageChange} required />
        </div>
        <div className='SubmitButton'>
          <button type='submit'>List this item</button>
        </div>
      </form>
    </div>
  );
}