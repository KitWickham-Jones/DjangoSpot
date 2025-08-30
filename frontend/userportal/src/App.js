import './App.css';
import { useState, useEffect } from 'react';
import { Button , ButtonGroup } from "@chakra-ui/react";
import { ChakraProvider} from "@chakra-ui/react";

const handleRedirect = () => {
	window.location.href = 'http://127.0.0.1:8000/spotify/login/'
}



function App(){
	return (
		<ChakraProvider>

			<div>
				<header className = 'app-header'>Spotify Data Aquisition </header>
				
			</div>
		</ChakraProvider>
	)

}

export default App;