import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import SignInSide from './components/SignUp.jsx'; 
import Response from './components/response.jsx';


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SignInSide />} />
        <Route path="/response" element={<Response />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
