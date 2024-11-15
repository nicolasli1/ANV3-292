const { EventBridgeClient, PutEventsCommand } = require('@aws-sdk/client-eventbridge');

const client = new EventBridgeClient({ region: 'us-east-1' }); // Set the region

async function putEventInEventBridge(orderDetails) {
  const detail = {
    restaurantName: orderDetails.restaurantName,
    order: orderDetails.order,
    customerName: orderDetails.name,
    amount: orderDetails.amount
  };

  const params = {
    Entries: [
      {
        Detail: JSON.stringify(detail),
        DetailType: 'order',
        Source: 'custom.orderManager'
      },
    ]
  };

  console.log(params);
  const command = new PutEventsCommand(params);
  return await client.send(command);
}

exports.putOrder = async (event) => {
  console.log('putOrder');

  const orderDetails = JSON.parse(event.body);
  const data = await putEventInEventBridge(orderDetails);

  return {
    statusCode: 200,
    body: JSON.stringify(orderDetails),
    headers: {}
  };
};
