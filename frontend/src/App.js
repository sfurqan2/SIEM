
import {useEffect, useState} from 'react';
import axios from 'axios';

function App() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:5000/api/v1/events").then(({data}) => {
      setEvents(data);
    })
  }, [])

  return (
    <div>
      {events.map((item, key) => (
        <div key={key}>
          {item.Name + " " + item.EventID + " " + item.Computer}
        </div>
      ))}
    </div>
  );
}

export default App;
