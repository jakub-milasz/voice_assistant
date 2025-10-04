const chatBox = document.getElementById("chat-box");
const micBtn = document.getElementById("mic-btn");
const sendBtn = document.getElementById("send-btn");
const userInput = document.getElementById("user-input");

// dodaje wiadomość do czatu
function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.classList.add(sender === "user" ? "user-message" : "bot-message");
    msg.textContent = text;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// wysyłanie tekstu
sendBtn.addEventListener("click", async () => {
    const text = userInput.value.trim();
    if (!text) return;

    addMessage(text, "user");
    userInput.value = "";

    // symulacja odpowiedzi (tu możesz połączyć z ML)
    const response = "Powiedziałeś: " + text;
    addMessage(response, "bot");

    // wywołaj endpoint odpowiedzi głosowej
    await fetch("/voice/respond", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: response }),
    });
});

// nagrywanie głosu
micBtn.addEventListener("click", async () => {
    addMessage("🎤 Nagrywam...", "bot");
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    const audioChunks = [];

    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
        const formData = new FormData();
        formData.append("file", audioBlob, "input.wav");

        const res = await fetch("/voice/recognize", {
            method: "POST",
            body: formData
        });
        const data = await res.json();

        addMessage("Ty: " + data.recognized_text, "user");

        // Odpowiedź asystenta
        const reply = "Zrozumiałem: " + data.recognized_text;
        addMessage(reply, "bot");

        await fetch("/voice/respond", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: reply }),
        });
    };

    mediaRecorder.start();
    setTimeout(() => mediaRecorder.stop(), 4 * 1000); // nagrywa 4 sekundy
});
