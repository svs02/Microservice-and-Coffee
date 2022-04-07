import React, { useEffect, useState } from 'react'
import '../App.css';

export default function Health() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getHealth = () => {
	
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
		const interval = setInterval(() => getHealth(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getHealth]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Health status</h1>
                <table className={"HealthTable"}>
					<tbody>
						<tr>
							<td>Receiver: {stats['receiver']}</td>
						</tr>
						<tr>
							<td>storage: {stats['storage']}</td>
						</tr>
                        <tr>
							<td>processing: {stats['processing']}</td>
						</tr>
                        <tr>
							<td>audit_log: {stats['audit_log']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>


            </div>
        )
    }
}
