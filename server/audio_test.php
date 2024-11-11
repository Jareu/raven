<?php
// Set your ElevenLabs API key
$elevenlabs_key = getenv('ELEVENLABS_API_KEY')

// Define the ElevenLabs API URL and headers
$url = "https://api.elevenlabs.io/v1/text-to-speech/aYnsKRtbVPhAk1n2Gz0r/stream";
$headers = [
    "xi-api-key: $elevenlabs_key",
    "Content-Type: application/json"
];

// Define the data payload for the API request
$data = [
    "text" => "Hello. This is a test.",
    "model_id" => "eleven_turbo_v2",
    "voice_settings" => [
        "stability" => 0.5,
        "similarity_boost" => 0.25
    ]
];

// Initialize cURL for the request
$ch = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, false);
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
curl_setopt($ch, CURLOPT_WRITEFUNCTION, function($curl, $data) {
    // Output the audio stream directly
    echo $data;
    return strlen($data);
});

// Set the appropriate content type for audio streaming
header("Content-Type: audio/mpeg");

curl_exec($ch);

// Check for errors
if (curl_errno($ch)) {
    echo "Error: " . curl_error($ch);
}

// Close the cURL session
curl_close($ch);
