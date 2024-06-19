import FileUpload from '../components/FileUpload';
import ImageResizer from '../components/ImageResizer';

export default function Home() {
    return (
        <div>
            <h1>PDF and DOCX to Ebook Converter</h1>
            <FileUpload />
            <h1>Image Resizer</h1>
            <ImageResizer />
        </div>
    );
}
