import { useState } from "react";
import Title from "./Title";
import axios from "axios";
import RecordMessage from "./RecordMessage";

const Controller = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);

  function createBlobURL(data: any) {
    const blob = new Blob([data], { type: "audio/mpeg" });
    return window.URL.createObjectURL(blob);
  }

  const handleStop = async (blobUrl: string) => {
    setIsLoading(true);
    console.log("Processing recorded audio...");

    try {
      const response = await fetch(blobUrl);
      const blob = await response.blob();
      console.log("Recorded Blob Size:", blob.size);

      if (blob.size === 0) {
        console.error("Error: Recorded blob is empty!");
        setIsLoading(false);
        return;
      }

      const formData = new FormData();
      formData.append("file", blob, "myFile.wav");

      const { data } = await axios.post("http://localhost:8000/post-audio", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      // Extract response data
      const { message_decoded, english_response, hindi_translation, audio_id } = data;

      console.log("🔹 Decoded Message:", message_decoded);
      console.log("🔹 English Response:", english_response);
      console.log("🔹 Hindi Translation:", hindi_translation);

      // Add User message
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "me", text: message_decoded, blobUrl },
      ]);

      // Fetch translated audio
      const audioResponse = await axios.get(`http://localhost:8000/get-audio/${audio_id}`, {
        responseType: "blob",
      });

      const audioBlob = audioResponse.data;
      const audioUrl = createBlobURL(audioBlob);
      const audioElement = new Audio(audioUrl);
      audioElement.play();

      // Add Translation message with Hindi text
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "Translation", blobUrl: audioUrl, text: english_response, hindi_text: hindi_translation },
      ]);
    } catch (error) {
      console.error("Error processing recorded audio:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen overflow-y-hidden">
      <Title setMessages={setMessages} />
      <div className="flex flex-col justify-between h-full overflow-y-scroll pb-96">
        <div className="mt-5 px-5">
          {messages.map((audio, index) => (
            <div key={index + audio.sender} className="flex flex-col w-full">
              <div className="mt-4 text-left w-full">
                {/* Show "me" messages on the left */}
                {audio.sender === "me" && (
                  <div className="flex justify-start w-full">
                    <div className="flex flex-col items-start">
                      <p className="italic text-blue-500">{audio.sender}</p>
                      <audio src={audio.blobUrl} className="appearance-none" controls />
                      {audio.text && (
                        <p className="mt-2 text-sm text-gray-700 font-semibold text-left flex bg-[#ddddddcc] p-2 rounded-tl-lg rounded-br-lg max-w-[80%] mx-auto">
                          {audio.text}
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* Show "Translation" messages in the center */}
                {audio.sender === "Translation" && (
                  <div className="flex justify-center items-center w-full">
                    <div className="flex flex-col items-center">
                      <p className="italic text-blue-500">{audio.sender}</p>
                      <audio src={audio.blobUrl} className="appearance-none" controls />
                      {audio.hindi_text && (
                        <p className="mt-2 text-sm text-gray-700 font-semibold text-center flex bg-[#ddddddcc] p-2 rounded-tl-lg rounded-br-lg max-w-[80%] mx-auto">
                          {audio.hindi_text}
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {messages.length === 0 && !isLoading && (
            <div className="text-center font-light italic mt-10">Say something...</div>
          )}

          {isLoading && (
            <div className="text-center font-light italic mt-10 animate-pulse">
              Gimme a few seconds...
            </div>
          )}
        </div>

        <div className="fixed bottom-10 right-10 bg-gray-900 text-white p-5 rounded-lg shadow-lg w-1/3">
          <p className="font-bold text-lg mb-4">CHAT RESPONSE</p>
          {messages.map((msg, index) =>
            msg.text ? (
              <div key={index} className="flex items-start bg-white text-black p-3 mt-2 rounded-lg max-w-[80%]">
                <img src={msg.sender === "me" ? "/user.png" : "/chatbot.png"} alt="Icon" className="w-8 h-8 rounded-full mr-3" />
                <div>
                  <p className="font-semibold">{msg.sender === "me" ? "User:" : "Chatbot:"}</p>
                  <p className={msg.sender === "me" ? "text-sm" : "text-sm italic"}>{msg.text}</p>
                </div>
              </div>
            ) : null
          )}
        </div>

        <div className="fixed bottom-0 w-full py-5 text-center">
          <div className="flex justify-center items-center w-full">
            <RecordMessage handleStop={handleStop} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Controller;
