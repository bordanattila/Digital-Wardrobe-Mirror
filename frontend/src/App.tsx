import './App.css'
import { UploadPage } from './pages/upload_clothing_item'
import { Routes, Route } from 'react-router-dom'
import { MirrorHome } from './pages/mirror'
import { FullWardrobe } from './pages/full_wardrobe'



function App() {
  return (
    <Routes>
      <Route path="/" element={<MirrorHome />} />
      <Route path="/upload" element={<UploadPage />} />
      <Route path="/full-wardrobe" element={<FullWardrobe />} />
    </Routes>
  )
}


export default App
