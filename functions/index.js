exports.handler = async function(event, context) {
  return {
    statusCode: 200,
    body: JSON.stringify({
      message: "Hello from index function!",
      path: event.path,
      method: event.httpMethod
    }),
    headers: {
      'Content-Type': 'application/json'
    }
  };
}; 