import { useState } from "react";
import { UserData } from "./UserData";
import Pagination from "./Pagination";




const UsersList = () => {

    const [currentpage,setCurrentpage] = useState(1)
    const [rows,setRows] = useState(20)

    const datalength = UserData.length;

    const handlenextclicK =  () => {
        setCurrentpage(currentpage+1);
    }

    const handlpreviousclicK =  () => {
        setCurrentpage(currentpage-1);
    }
    const startIndex = (currentpage-1)* rows;
    const endIndex = startIndex + rows;
    const paginated_data = UserData.filter((user,index)=> index >= startIndex && index < endIndex)
    
    return(
        <>
        <table className="table border-blue-200 w-full">
            <thead>
            <tr className="border ">
                <th className="text-left border border-gray-400 bg-gray-200">Id</th>
                <th className="text-left border bg-gray-200 border-gray-400">Name</th>
                <th className="text-left border border-gray-400 bg-gray-200">Email</th>
            </tr>
            </thead>
            <tbody>
                {paginated_data.map(user =>  (
                    <tr key={user.id}>
                        <td className="border">{user.id}</td>
                        <td className="border">{user.name}</td>
                        <td className="border">{user.email}</td>
                    </tr>
                ))}
            </tbody>
        </table>
        <div className="mt-8 mb-4">
        <Pagination
         datalength={datalength} currentpage={currentpage} rows={rows} UserData={UserData}
          handlenextclick={handlenextclicK} handlpreviousclicK={handlpreviousclicK}/>
          </div>
        
          </>
    )
}

export default UsersList;