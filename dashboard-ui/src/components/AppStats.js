import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://kafka3855.eastus.cloudapp.azure.com:8100/processing/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
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
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Location</th>
							<th>Flavour</th>
						</tr>
						<tr>
							<td># L: {stats['num_location_phone_readings']}</td>
							<td># F: {stats['max_flavour_points_reading']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Flavour review: {stats['num_flavour_review_count_readings']}</td>
						</tr>
						<tr>
							<td colspan="2">Max location number: {stats['num_location_Countrycode_number_readings']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>


            </div>
        )
    }
}
