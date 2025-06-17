import Menu from "../Components/Menu";
import {Routes,Route,BrowserRouter as Router} from "react-router-dom";
import UsersList from "../Components/UsersList";


const AdminPage = () =>{
     return(
        <>
          <main className="mainAdmin h-screen">
            <Menu/>
            <div className="content w-full">
            <Routes>
              <Route path="users" element={<UsersList/>}></Route>
            </Routes>
            </div>
          </main>
        </>
     )
}

export default AdminPage;