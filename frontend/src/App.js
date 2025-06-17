import React, { useState } from 'react';
import './App.css';
import {Routes,Route,BrowserRouter as Router} from "react-router-dom";
import AdminPage from './Pages/AdminPage';

const App = () => {

    const [access,setAccess] = useState(false);

  return (
      <Router>
          <Routes>
              <Route path="/admin/*" element={<AdminPage/>}></Route>
          </Routes>
      </Router>
  );
};


export default App;
