import { useState } from 'react';

export default function App() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([
    { id: '1', content: 'Hello! I can see this message clearly.', isUser: false }
  ]);

  const sendMessage = () => {
    if (!message.trim()) return;
    
    const userMessage = { id: Date.now().toString(), content: message, isUser: true };
    setMessages(prev => [...prev, userMessage]);
    setMessage('');
    
    // AI回复
    setTimeout(() => {
      const aiMessage = { 
        id: (Date.now() + 1).toString(), 
        content: `You said: "${message}". This is working!`, 
        isUser: false 
      };
      setMessages(prev => [...prev, aiMessage]);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">
          🤖 AI Assistant - Test
        </h1>
        
        <div className="bg-white rounded-lg shadow-lg mb-4 h-96 overflow-y-auto p-4">
          {messages.map((msg) => (
            <div key={msg.id} className={`mb-4 flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                msg.isUser 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-200 text-gray-800'
              }`}>
                {msg.content}
              </div>
            </div>
          ))}
        </div>
        
        <div className="bg-white rounded-lg shadow-lg p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Type a test message..."
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={sendMessage}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              Send
            </button>
          </div>
        </div>
        
        <div className="mt-4 text-center text-gray-600">
          <p>✅ If you can see this, the page is working!</p>
        </div>
      </div>
    </div>
  );
}
