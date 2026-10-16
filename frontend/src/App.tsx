import './App.css'
import { UploadPage } from './pages/upload_clothing_item'
import { Routes, Route } from 'react-router-dom'
import { MirrorHome } from './pages/mirror'



function App() {
  return (
    <Routes>
      <Route path="/" element={<MirrorHome />} />
      <Route path="/upload" element={<UploadPage />} />
    </Routes>
  )
}


export default App
