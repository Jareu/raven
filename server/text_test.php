<?php
// Set your OpenAI API key
$openai_key = getenv('OPENAI_API_KEY');

// Define the OpenAI API endpoint and headers
$url = "https://api.openai.com/v1/chat/completions";
$headers = [
    "Authorization: Bearer " . $openai_key,
    "Content-Type: application/json"
];

// Define the data payload for the API request
$data = [
    "model" => "gpt-4o-mini",
    "temperature" => 0.7,
    "max_tokens" => 50,
    "messages" => [
		[
			"role"    => "user",
			"content" => "Write me a limerick about vikings."
		]
	]
];

// Initialize curl
$ch = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));

// Execute the request and handle errors
$response = curl_exec($ch);
if (curl_errno($ch)) {
    echo "Error: " . curl_error($ch);
    exit;
}

// Close the curl session
curl_close($ch);

// Parse the JSON response and display the result
$result = json_decode($response, true);

if (isset($result['choices'][0]['message']['content'])) {
    echo "<h3>Here's your Viking Limerick:</h3>";
    echo "<p>" . nl2br(htmlspecialchars($result['choices'][0]['message']['content'])) . "</p>";
} else {
    echo "<p>Error: Unable to get a response from OpenAI.</p><div>" . $response ."</div>";
}
