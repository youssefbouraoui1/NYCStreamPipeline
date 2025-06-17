import { useState } from "react"



const Pagination = ({datalength,rows,currentpage,UserData,handlenextclick,handlpreviousclicK}) => {
    
    

    

    

    return(
        <div className="flex justify-center pb-4">
        <button type="submit" className="p-2 border border-blue-400 rounded disabled:cursor-not-allowed disabled:opacity-50" disabled={currentpage===1} onClick={()=>handlpreviousclicK()}>previous</button>
        <button className="ml-4 text-center">{currentpage}</button>
        <button type="submit" className="ml-4 p-2 border border-blue-400 rounded disabled:cursor-not-allowed disabled:opacity-50" disabled={currentpage===Math.ceil(datalength/rows)} onClick={()=>handlenextclick()}>next</button>
        </div>
    )
        
    
}

export default Pagination;