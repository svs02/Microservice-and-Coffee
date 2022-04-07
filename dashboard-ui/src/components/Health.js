import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://kafka3855.eastus.cloudapp.azure.com/health`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received health")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"HealthTable"}>
					<tbody>
						<tr>
							<th>Health status</th>
						</tr>
						<tr>
							<td>Receiver: {stats['receiver']}</td>
                            <td>Receiver: {stats['storage']}</td>
                            <td>Receiver: {stats['processing']}</td>
                            <td>Receiver: {stats['audit_log']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>


            </div>
        )
    }
}
