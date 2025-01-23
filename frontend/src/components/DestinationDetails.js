import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './DestinationDetails.css';

function DestinationDetails({ destinationId }) {
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Update the URL to match your Django backend
                const res = await axios.get(`http://localhost:7000/api/destination/${destinationId}/`);
                setData(res.data);
            } catch (error) {
                console.error(error);
                setError('Failed to fetch destination details');
            }
        };

        fetchData();
    }, [destinationId]);

    if (error) {
        return <p className="error">{error}</p>;
    }

    if (!data) {
        return (
            <div className="loading">
                <p>Loading destination details...</p>
                <div className="spinner"></div>
            </div>
        );
    }

    return (
        <div className="destination-details">
            <div className="destination-header">
                <h2>{data.destination.name} ({data.destination.city})</h2>
                <p className="destination-description">{data.destination.description}</p>
            </div>

            <div className="destination-meta">
                <h3>Best Time to Visit</h3>
                <p>{data.destination.best_time_to_visit}</p>
                <h4>Tags:</h4>
                <ul className="destination-tags">
                    {data.destination.tags && data.destination.tags.length > 0 ? (
                        data.destination.tags.map((tag, index) => (
                            <li key={index} className="tag-item">{tag}</li>
                        ))
                    ) : (
                        <p>No tags available for this destination.</p>
                    )}
                </ul>
            </div>

            <div className="destination-places">
                <h3>Places to Explore</h3>
                {data.places.length > 0 ? (
                    <ul>
                        {data.places.map((place, index) => (
                            <li key={index} className="place-item">
                                <h4>{place.name} ({place.category || 'General'})</h4>
                                <p>{place.description}</p>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p>No places found for this destination.</p>
                )}
            </div>

            <div className="destination-food">
                <h3>Local Cuisine</h3>
                {data.food.length > 0 ? (
                    <ul>
                        {data.food.map((foodItem, index) => (
                            <li key={index} className="food-item">
                                <h4>{foodItem.name} ({foodItem.cuisine_type || 'General'})</h4>
                                <p>{foodItem.description}</p>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p>No local food information available.</p>
                )}
            </div>
        </div>
    );
}

export default DestinationDetails;
