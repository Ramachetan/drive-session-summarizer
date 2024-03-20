import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import './Response.css'; 
import MiracleLogo from '../assets/Miracle Logo.svg';
import gemini from '../assets/gemini.svg';
import axios from 'axios';
import SideLogo from '../assets/Group.svg';

const ApiResponsePage = () => {
  const location = useLocation();
  const apiResponse = location.state?.apiResponse;
  const player_id = location.state?.player_id;
  console.log("dsfoinaosfn",player_id);

  const [messages, setMessages] = useState([]);

  const handleSubmit = async (event) => {
  event.preventDefault();
  const messageText = event.target.elements.name.value; // Assuming 'name' is the name of your input field

  const newMessage = { id: Date.now(), text: messageText, type: 'user' };
  setMessages([...messages, newMessage]);

  try {
    const response = await axios.post('http://127.0.0.1:8000/chat', {
  message: messageText,  
  player_id: player_id  
}, {
  headers: {
    'Content-Type': 'application/json'
  }
});



    const apiResponse = { id: Date.now(), text: response.data.response, type: 'api' };
    setMessages(currentMessages => [...currentMessages, apiResponse]);
  } catch (error) {
    console.error(error);
  }
};

  return (
    <div className="apiResponseContainer">
      <header className="header">
        <div className="logo">
          <img src={MiracleLogo} alt="Miracle Logo" style={{ width: '180px', height: '140px' }} />
        </div>
      </header>
      
      <div className="contentContainer">
        <div className="markdownContainer">
          {apiResponse ? (
            <ReactMarkdown>{apiResponse}</ReactMarkdown>
          ) : (
            <p>No response received.</p>
          )}
        </div>
      
        
        <div className="chatContainer">
 <div className="messages">
  {messages.map((msg) => (
    <div key={msg.id} className={`message ${msg.type}`}>
      {msg.type === 'user' ? <b>User: </b> : <b>Gemini: </b>}
      {msg.text}
    </div>
  ))}
</div>
  <form className="chatBox" onSubmit={handleSubmit}>
    <input type="text" id="name" name="name" placeholder="Type your message here" />
    <button type="submit">Send</button>
  </form>
</div>


      </div>
      <footer className="apiResponseFooter">
        <div className="footerText">
          <img src={gemini} alt="Gemini" />
        </div>
      </footer>
    </div>
  );
};

export default ApiResponsePage;
