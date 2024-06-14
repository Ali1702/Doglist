import React, { useState, useEffect } from "react";
import AddDogForm from "./components/AddDogForm";
import DogList from "./components/DogList";
import Keycloak from "keycloak-js";

const initOptions = {
    url: "http://localhost:8080/",
    realm: "MyRealm",
    clientId: "doglist-client",
};

const kc = new Keycloak(initOptions);

const initializeKeycloak = async () => {
    const authenticated = await kc.init({
        onLoad: "login-required",
        checkLoginIframe: true,
    });

    if (authenticated) {
        console.log("User is authenticated");
        localStorage.setItem("token", kc.token);
        localStorage.setItem("refreshToken", kc.refreshToken);

        kc.onTokenExpired = () => {
            console.log("token expired");
            kc.updateToken(30).success((refreshed) => {
                if (refreshed) {
                    localStorage.setItem("token", kc.token);
                    localStorage.setItem("refreshToken", kc.refreshToken);
                }
            });
        };

        return true;
    } else {
        console.log("User is not authenticated");
        window.location.reload();
    }

    return false;
};

function App() {
    const [authenticated, setAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);
    const [kcInitialized, setKcInitialized] = useState(false);

    useEffect(() => {
        const initAuth = async () => {
            if (!kcInitialized) {
                const auth = await initializeKeycloak();
                setAuthenticated(auth);
                setKcInitialized(true);
                setLoading(false);
            }
        };

        initAuth();
    }, [kcInitialized]);

    if (loading) {
        return <div>Loading...</div>;
    }

    if (authenticated) {
        localStorage.setItem("token", kc.token);
        localStorage.setItem("refreshToken", kc.refreshToken);
    }

    return (
        <div className="App">
            <h1>Dog Management</h1>
            <AddDogForm />
            <DogList />
            <button onClick={() => kc.logout({ redirectUri: "http://localhost:3000/" })}>
                Logout
            </button>
        </div>
    );
}

export default App;
