import React, { useEffect, useState } from "react";
import axios from "axios";

const DogList = () => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL;

    const [dogs, setDogs] = useState([]);

    useEffect(() => {
        const token = localStorage.getItem("token");
        axios
            .get(`${backendUrl}/dogs`, {
                headers: {
                    Authorization: "Bearer " + token,
                },
            })
            .then((response) => {
                setDogs(response.data);
            })
            .catch((error) => {
                console.error("Error fetching data: ", error);
            });
    }, []);

    return (
        <div>
            <h2>Dogs</h2>
            <ul>
                {dogs.map((dog) => (
                    <li key={dog.id}>
                        {dog.name} - {dog.breed}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default DogList;
