import { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [events, setEvents] = useState([]);
  const [modalVisible, setModalVisibility] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);

  useEffect(() => {
    axios.get("http://localhost:5000/").then(({ data }) => {
      setEvents(data);
    });
  }, []);

  function handleAlert(eventType) {
    switch (eventType) {
      case 1:
        return "Created";
      case 2:
        return "Deleted";
      default:
        return "";
    }
  }

  function renderModal() {
    if (modalVisible && selectedAlert)
      return (
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-3/4 h-full flex items-center justify-center">
          <div className="shadow-md w-full">
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <div className="px-4 py-5 sm:px-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  Alert Information
                </h3>
                <p className="mt-1 max-w-2xl text-sm text-gray-500">
                  Details about the threat.
                </p>
              </div>
              <div className="border-t border-gray-200">
                <dl>
                  <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt className="text-sm font-medium text-gray-500">Label</dt>
                    <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-600">
                        Information Theft
                      </span>
                    </dd>
                  </div>

                  <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt className="text-sm font-medium text-gray-500">
                      Individual Details
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                      <ul className="border border-gray-200 rounded-md divide-y divide-gray-200">
                        {selectedAlert.details.map((alert, key) => (
                          <li
                            key={key}
                            className="pl-3 pr-4 py-3 flex items-center justify-between text-sm"
                          >
                            <div className="w-0 flex-1 flex items-center">
                              <span className="ml-2 flex-1 w-0 truncate">
                                {alert[0]}
                              </span>
                              <span className="ml-2 flex-1 w-0 truncate">
                                {handleAlert(alert[1])}
                              </span>
                              <span className="ml-2 flex-1 w-0 truncate">
                                {alert[3]}
                              </span>
                            </div>
                          </li>
                        ))}
                      </ul>
                    </dd>
                  </div>
                </dl>
                <div className="flex justify-end m-5">
                  <button
                    className="py-2 px-4 bg-red-500 text-white rounded"
                    onClick={() => setModalVisibility(false)}
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      );
  }

  return (
    /* This example requires Tailwind CSS v2.0+ */
    <div>
      {renderModal()}
      <div className="flex flex-col max-w-7xl mt-5 mx-auto">
        <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
            <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th
                      scope="col"
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      Filename/Dirname
                    </th>
                    <th
                      scope="col"
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      Datetime
                    </th>
                    <th
                      scope="col"
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      Label
                    </th>
                    <th scope="col" className="relative px-6 py-3">
                      <span className="sr-only">Edit</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {events.map((event, key) => (
                    <tr key={key}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {event.files.map((file, key) => (
                            <p key={key}>{file}</p>
                          ))}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {event.time}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-600">
                          Information Theft
                        </span>
                      </td>

                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => {
                            setSelectedAlert(event);
                            setModalVisibility(true);
                          }}
                        >
                          Show Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
