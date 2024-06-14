import React, { useState } from "react";
import axios from "axios";

const AddDogForm = () => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL;

    const [name, setName] = useState("");
    const [breed, setBreed] = useState("");

    const handleSubmit = (event) => {
        event.preventDefault();

        const token = localStorage.getItem("token");

        axios
            .post(
                `${backendUrl}/dogs`,
                {
                    name: name,
                    breed: breed,
                },
                {
                    headers: {
                        Authorization: "Bearer " + token,
                    },
                }
            )
            .then((response) => {
                console.log("Dog added successfully");
                setName("");
                setBreed("");
                window.location.reload();
            })
            .catch((error) => {
                console.error("Error adding dog: ", error);
            });
    };

    return (
        <div>
            <h2>Add Dog</h2>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Name:</label>
                    <input
                        type="text"
                        value={name}
                        onChange={(event) => setName(event.target.value)}
                        required
                    />
                </div>
                <div>
                    <label>Breed:</label>
                    <input
                        type="text"
                        value={breed}
                        onChange={(event) => setBreed(event.target.value)}
                        required
                    />
                </div>
                <button type="submit">Add Dog</button>
            </form>
        </div>
    );
};

export default AddDogForm;
