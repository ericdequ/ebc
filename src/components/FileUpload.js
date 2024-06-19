import { useState } from 'react';

export default function FileUpload() {
    const [file, setFile] = useState(null);
    const [width, setWidth] = useState(800);
    const [height, setHeight] = useState(600);

    // Handle file selection
    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    // Handle width input change
    const handleWidthChange = (e) => {
        setWidth(e.target.value);
    };

    // Handle height input change
    const handleHeightChange = (e) => {
        setHeight(e.target.value);
    };

    // Handle form submission for file upload
    const handleSubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('file', file);
        formData.append('width', width);
        formData.append('height', height);
        
        const response = await fetch('http://localhost:5000/upload', {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();
        console.log(result);
    };

    return (
        <div>
            <h1>Upload your file</h1>
            <form onSubmit={handleSubmit}>
                <input type="file" onChange={handleFileChange} />
                <label>
                    Width:
                    <input type="number" value={width} onChange={handleWidthChange} />
                </label>
                <label>
                    Height:
                    <input type="number" value={height} onChange={handleHeightChange} />
                </label>
                <button type="submit">Upload</button>
            </form>
        </div>
    );
}
