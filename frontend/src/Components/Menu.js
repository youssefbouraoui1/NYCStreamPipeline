import React, { useState } from "react";
import { MenuData } from "./MenuData";
import { Link } from "react-router-dom";
import MenuIcon from '@mui/icons-material/Menu';

const Menu = ()=>{

  const [visible,setVisible]= useState(true);

  const toggleMenu = () => {
       setVisible(!visible);
  }

    return (
      <div className={`h-full ${visible?"adminmenuvisible bg-gray-200 pr-2":"adminmenuhidden bg-gray-200 pr-2"}`} >
        <button className="ml-4 pb-4" onClick={toggleMenu}><MenuIcon/>{visible?"Menu":""}</button>
        <ul className={visible?"":"hidden"}>
          {MenuData.map(data=>(
            <li key={data.id} className="pl-2 pr-2 ml-4 mb-4 hover:bg-gray-300 rounded">
              <Link to={data.path}>
                <span>{data.title}</span>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    );
};

export default Menu;