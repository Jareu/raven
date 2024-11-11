<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");

class RavenServer {
    private $openai_key;
    private $elevenlabs_key;

    public function __construct() {
        $this->openai_key = getenv('OPENAI_API_KEY');
        $this->elevenlabs_key = getenv('ELEVENLABS_API_KEY');
        $this->prompt = <<<'EOD'
Respond as Huginn, Odin's all-seeing raven, who speaks with the voice of
ancient wisdom and mystery. Huginn is wise, cryptic, and poetic, often seeing
deep into the soul of those who seek his guidance. Huginn's words should be
filled with Norse imagery, drawing from nature, mythology, and the shadows of fate.
Your words should echo with Norse mythology and be shrouded in ambiguity, each
sentence crafted to feel both specific and universal. Speak as though you see
what the seeker cannot, hinting at their inner struggles and offering advice
that resonates deeply. Answer the question directly, in a few words. Then follow up with one or two sentences.
make use of Barnum statements and avoid specifics; instead, speak of ‘paths,’ ‘shadows,’ ‘winds of change,’ or
the fires of dawn.’ Keep the tone wise, solemn, and slightly ominous.
Reference ancient wisdom, then provide an answer. Responses should be short,
no more than 1 or 2 sentences, with an air of solemnity and depth.
EOD;
    }

    public function handleRequest() {
        $path = parse_url($_SERVER["REQUEST_URI"], PHP_URL_PATH);
        
        if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
            http_response_code(204);
            exit;
        }
        
        $path = str_replace($_SERVER['SCRIPT_NAME'], "", $path); // Remove base path
        
        if ($path === '/get_fortune' && $_SERVER['REQUEST_METHOD'] === 'POST') {
            $this->getFortune();
        } elseif ($path === '/get_fortune_audio' && $_SERVER['REQUEST_METHOD'] === 'POST') {
            $this->getFortuneAudio();
        } else {
            http_response_code(404);
            echo json_encode(["error" => sprintf("Path %s not found", $path)]);
        }
    }

    private function getFortune() {
        $input = json_decode(file_get_contents("php://input"), true);
        $question = $input['question'] ?? null;

        if (!$question) {
            http_response_code(400);
            echo json_encode(["error" => "Question not provided"]);
            return;
        }

        try {
            $responseText = $this->generateResponseText($question);
            echo json_encode(["text" => $responseText]);
        } catch (Exception $e) {
            http_response_code(500);
            echo json_encode(["error" => "Internal server error"]);
        }
    }

    private function getFortuneAudio() {
        $input = json_decode(file_get_contents("php://input"), true);
        $text = $input['text'] ?? null;

        if (!$text) {
            http_response_code(400);
            echo json_encode(["error" => "Text not provided"]);
            return;
        }

        try {
            header("Content-Type: audio/mpeg");
            $this->generateAudioStream($text);
        } catch (Exception $e) {
            http_response_code(500);
            echo json_encode(["error" => "Internal server error"]);
        }
    }

    private function generateResponseText($question) {
        try {
        $url = "https://api.openai.com/v1/chat/completions";
        
        $headers = [
            "Authorization: Bearer " . $this->openai_key,
            "Content-Type: application/json"
        ];
        
        $data = [
            "model" => "gpt-4",
            "messages" => [
                [
                    "role" => "system",
                    "content" => [
                        [
                            "type" => "text",
                            "text" => $this->prompt
                        ]
                    ]
                ],
                [
                    "role" => "user",
                    "content" => [
                        [
                            "type" => "text",
                            "text" => $question
                        ]
                    ]
                ]
            ],
            "temperature" => 1,
            "max_tokens" => 100
        ];
        
        $response = $this->makeCurlRequest($url, $headers, $data);
        return $response['choices'][0]['message']['content'] ?? "No response from OpenAI.";
        server_log(var_dump($response));
        
        } catch (exception $ex) {
            http_response_code(500);
            echo json_encode(["exception" => $ex]);
        }
    }

    private function generateAudioStream($text) {
        $url = "https://api.elevenlabs.io/v1/text-to-speech/aYnsKRtbVPhAk1n2Gz0r/stream";
        $headers = [
            "xi-api-key: " . $this->elevenlabs_key,
            "Content-Type: application/json"
        ];
        $data = [
            "text" => $text,
            "model_id" => "eleven_turbo_v2",
            "voice_settings" => [
                "stability" => 0.5,
                "similarity_boost" => 0.25
            ]
        ];

        $this->streamCurlRequest($url, $headers, $data);
    }

    private function makeCurlRequest($url, $headers, $data) {
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        
        $response = curl_exec($ch);
        if (curl_errno($ch)) {
            throw new Exception("Curl error: " . curl_error($ch));
        }

        curl_close($ch);
        
        return json_decode($response, true);
    }

    private function streamCurlRequest($url, $headers, $data) {
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, false);
        curl_setopt($ch, CURLOPT_WRITEFUNCTION, function($curl, $data) {
            echo $data;
            return strlen($data);
        });

        curl_exec($ch);
        if (curl_errno($ch)) {
            throw new Exception("Curl error: " . curl_error($ch));
        }

        curl_close($ch);
    }
}

function server_log($log_msg)
{
    $log_filename = "raven_server";
    if (!file_exists($log_filename)) 
    {
        // create directory/folder uploads.
        mkdir($log_filename, 0777, true);
    }
    $log_file_data = $log_filename.'/log_' . date('d-M-Y') . '.log';
    // if you don't add `FILE_APPEND`, the file will be erased each time you add a log
    file_put_contents($log_file_data, $log_msg . "\n", FILE_APPEND);
} 

$server = new RavenServer();
$server->handleRequest();
