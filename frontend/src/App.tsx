import { Routes, Route } from 'react-router-dom';
import { ProcessPage } from './pages/ProcessPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<ProcessPage />} />
    </Routes>
  );
}

export default App;
