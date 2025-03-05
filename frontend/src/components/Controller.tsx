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

    // Convert blob URL to blob object
    fetch(blobUrl)
      .then((res) => res.blob())
      .then(async (blob) => {
        console.log("Recorded Blob Size:", blob.size);
        if (blob.size === 0) {
          console.error("Error: Recorded blob is empty!");
          setIsLoading(false);
          return;
        }

        // Append recorded message to messages
        const myMessage = { sender: "me", blobUrl };
        const messagesArr = [...messages, myMessage];
        setMessages(messagesArr);

        // Send audio to backend
        const formData = new FormData();
        formData.append("file", blob, "myFile.wav");

        try {
          const response = await axios.post("http://localhost:8000/post-audio", formData, {
            headers: { "Content-Type": "multipart/form-data" },
            responseType: "arraybuffer",
          });

          // Convert response to audio and play it
          const audioBlob = new Blob([response.data], { type: "audio/mpeg" });
          const audioUrl = createBlobURL(audioBlob);
          const rachelMessage = { sender: "rachel", blobUrl: audioUrl };

          setMessages([...messagesArr, rachelMessage]);
          setIsLoading(false);

          const audio = new Audio(audioUrl);
          audio.play();
        } catch (error) {
          console.error("Error sending audio:", error);
          setIsLoading(false);
        }
      })
      .catch((error) => {
        console.error("Error processing recorded audio:", error);
        setIsLoading(false);
      });
  };

  return (
    <div className="h-screen overflow-y-hidden">
      {/* Title */}
      <Title setMessages={setMessages} />

      <div className="flex flex-col justify-between h-full overflow-y-scroll pb-96">
        {/* Conversation */}
        <div className="mt-5 px-5">
          {messages.map((audio, index) => (
            <div
              key={index + audio.sender}
              className={"flex flex-col " + (audio.sender === "rachel" && "flex items-end")}
            >
              <div className="mt-4 ">
                <p
                  className={
                    audio.sender === "Translation"
                      ? "text-right mr-2 italic text-green-500"
                      : "ml-2 italic text-blue-500"
                  }
                >
                  {audio.sender}
                </p>

                <audio src={audio.blobUrl} className="appearance-none" controls />
              </div>
            </div>
          ))}

          {messages.length === 0 && !isLoading && (
            <div className="text-center font-light italic mt-10">
              Say something...
            </div>
          )}

          {isLoading && (
            <div className="text-center font-light italic mt-10 animate-pulse">
              Gimme a few seconds...
            </div>
          )}
        </div>

        {/* Recorder */}
        <div className="fixed bottom-0 w-full py-6 border-t text-center bg-gradient-to-r from-yellow-500 to-yellow-100">
          <div className="flex justify-center items-center w-full">
            <div>
              <RecordMessage handleStop={handleStop} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Controller;
