import {
  useState,
  useRef,
  useEffect,
} from "react";

import axios from "axios";
import ReactMarkdown from "react-markdown";

import {
  FaArrowUp,
  FaGithub,
  FaLinkedin,
  FaEnvelope,
  FaDownload,
} from "react-icons/fa";

import tushitImage from "./assets/tushit.png";

function App() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] =
    useState([]);
  const [loading, setLoading] =
    useState(false);

  const [chatStarted, setChatStarted] =
    useState(false);

  const messagesContainerRef =
    useRef(null);

  const [isMobile, setIsMobile] =
    useState(
      window.innerWidth <= 768
    );

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(
        window.innerWidth <= 768
      );
    };

    window.addEventListener(
      "resize",
      handleResize
    );

    return () =>
      window.removeEventListener(
        "resize",
        handleResize
      );
  }, []);

  const quickPrompts = [
    "Tell me about Tushit",
    "Summarize his experience",
    "What projects has he built?",
    "What tech stacks does he know?",
    "What are his technical skills?",
    "How can I contact him?",
  ];

  useEffect(() => {
    const container =
      messagesContainerRef.current;

    if (container) {
      setTimeout(() => {
        container.scrollTo({
          top: container.scrollHeight,
          behavior: "smooth",
        });
      }, 100);
    }
  }, [messages, loading]);

  const typeMessage = (
    fullText,
    callback
  ) => {
    let index = 0;

    const interval =
      setInterval(() => {
        index++;

        callback(
          fullText.slice(0, index)
        );

        if (
          index >= fullText.length
        ) {
          clearInterval(interval);
        }
      }, 8);
  };

  const askQuestion = async (
    questionText = query
  ) => {
    if (!questionText.trim()) return;

    setChatStarted(true);

    const userMessage = {
      type: "user",
      text: questionText,
    };

    setMessages((prev) => [
      ...prev,
      userMessage,
    ]);

    setLoading(true);
    setQuery("");

    try {
      const response = await axios.post(
        "https://tushit-ai-backend.onrender.com/chat",
        {
          query: questionText,
        }
      );

      const fullResponse =
        response.data.response ||
        "No response generated.";

      const botMessage = {
        type: "bot",
        text: "",
      };

      setMessages((prev) => [
        ...prev,
        botMessage,
      ]);

      typeMessage(
        fullResponse,
        (typedText) => {
          setMessages((prev) => {
            const updated = [
              ...prev,
            ];

            updated[
              updated.length - 1
            ] = {
              type: "bot",
              text: typedText,
            };

            return updated;
          });
        }
      );
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          text: "Unable to connect to backend.",
        },
      ]);
    }

    setLoading(false);
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at top right, rgba(255,204,0,0.18), transparent 35%), #000000",
        color: "white",
        fontFamily:
          "Inter, system-ui, sans-serif",
        overflow: "hidden",
        position: "relative",
      }}
    >
      <style>
        {`
          @keyframes floating {
            0% {
              transform: translateY(0px);
            }

            50% {
              transform: translateY(-12px);
            }

            100% {
              transform: translateY(0px);
            }
          }

          @keyframes fadeUp {
            from {
              opacity: 0;
              transform: translateY(60px);
              filter: blur(8px);
            }

            to {
              opacity: 1;
              transform: translateY(0);
              filter: blur(0);
            }
          }

          ::-webkit-scrollbar {
            width: 6px;
          }

          ::-webkit-scrollbar-thumb {
            background: #ffcc00;
            border-radius: 999px;
          }

          @keyframes typing {
            from {
              width: 0;
            }

            to {
              width: 14ch;
            }
          }

          @keyframes blink {
            50% {
              border-color: transparent;
            }
          }

          .typing-logo {
            animation:
              typing 2.4s steps(14),
              blink 0.8s infinite;
          }
        `}
      </style>

      {/* TOP BAR */}
      <div
        style={{
          display: "flex",
          justifyContent:
            "space-between",
          alignItems: "center",
          padding: isMobile
            ? "20px 18px"
            : "34px 44px",
          animation:
            "fadeUp 0.8s ease",
          position: "relative",
          zIndex: 10,
        }}
      >
        <div>
          <h1
            className="typing-logo"
            style={{
              margin: 0,
              fontSize: isMobile
                ? "1.5rem"
                : "2.2rem",
              fontWeight: 800,
              letterSpacing: "-1px",
              color: "#ffffff",
              whiteSpace: "nowrap",
              overflow: "hidden",
              borderRight:
                "3px solid #ffcc00",
              width: "fit-content",
            }}
          >
            {"</Tushit.dev>"}
          </h1>

          <p
            style={{
              color: "#8b8b8b",
              marginTop: "10px",
              fontSize: isMobile
                ? "0.82rem"
                : "1rem",
              letterSpacing: "0.3px",
            }}
          >
            AI Portfolio Assistant
          </p>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: isMobile
              ? "10px"
              : "16px",
          }}
        >
          <a
            href="https://github.com/tushit24"
            target="_blank"
            rel="noreferrer"
            style={{
              ...iconStyle,
              width: isMobile
                ? "44px"
                : "58px",
              height: isMobile
                ? "44px"
                : "58px",
              fontSize: isMobile
                ? "1rem"
                : "1.2rem",
            }}
          >
            <FaGithub />
          </a>

          <a
            href="https://www.linkedin.com/in/tushit-tiwari-97431928a/"
            target="_blank"
            rel="noreferrer"
            style={{
              ...iconStyle,
              width: isMobile
                ? "44px"
                : "58px",
              height: isMobile
                ? "44px"
                : "58px",
              fontSize: isMobile
                ? "1rem"
                : "1.2rem",
            }}
          >
            <FaLinkedin />
          </a>

          <a
            href="mailto:rishitiwariofficial@gmail.com"
            style={{
              ...iconStyle,
              width: isMobile
                ? "44px"
                : "58px",
              height: isMobile
                ? "44px"
                : "58px",
              fontSize: isMobile
                ? "1rem"
                : "1.2rem",
            }}
          >
            <FaEnvelope />
          </a>

          {!isMobile && (
            <a
              href="/Tushit_Tiwari_ATS_Resume 106.pdf"
              download
              style={{
                background:
                  "#ffcc00",
                color: "black",
                padding:
                  "16px 28px",
                borderRadius:
                  "18px",
                textDecoration:
                  "none",
                fontWeight: 700,
                display: "flex",
                alignItems:
                  "center",
                gap: "10px",
              }}
            >
              <FaDownload />
              Resume
            </a>
          )}
        </div>

        {/* MOBILE RESUME BUTTON */}
        {isMobile && (
          <div
            style={{
              position: "absolute",
              top: "131px",
              left: "50%",
              transform: "translateX(-50%)",
              zIndex: 20,
            }}
          >
            <a
              href="/Tushit_Tiwari_ATS_Resume 106.pdf"
              download
              style={{
                background: "#ffcc00",
                color: "black",
                padding: "10px 18px",
                borderRadius: "14px",
                textDecoration: "none",
                fontWeight: 700,
                display: "flex",
                alignItems: "center",
                gap: "8px",
                fontSize: "0.88rem",
                boxShadow:
                  "0 8px 30px rgba(255,204,0,0.25)",
              }}
            >
              <FaDownload />
              Resume
            </a>
          </div>
        )}
      </div>

      {/* MAIN BODY */}
      <div
        style={{
          height:
            "calc(100vh - 130px)",
          position: "relative",
        }}
      >
        {!chatStarted ? (
          <div
            style={{
              height: "100%",
              display: "grid",
              gridTemplateColumns:
                isMobile
                  ? "1fr"
                  : "1.05fr 0.95fr",
              alignItems: "center",
              padding: isMobile
                ? "20px 18px 180px"
                : "0 44px 300px 44px",
              gap: "30px",
            }}
          >
            {/* LEFT */}
            <div
              style={{
                transform:
                  isMobile
                    ? "translateY(0)"
                    : "translateY(-55px)",
                animation:
                  "fadeUp 1s ease 0.4s both",
                position: "relative",
                zIndex: 5,
                textAlign: isMobile
                  ? "center"
                  : "left",
              }}
            >
              <h1
                style={{
                  margin: 0,
                  lineHeight: 0.95,
                  fontSize: isMobile
                    ? "3rem"
                    : "5rem",
                  fontWeight: 900,
                  letterSpacing:
                    isMobile
                      ? "-2px"
                      : "-4px",
                }}
              >
                <span
                  style={{
                    color: "white",
                  }}
                >
                  I'm{" "}
                </span>

                <span
                  style={{
                    color:
                      "#ffcc00",
                  }}
                >
                  Tushit,
                </span>

                <br />

                <span
                  style={{
                    color: "white",
                  }}
                >
                  Tech Enthusiast
                </span>
              </h1>

              <p
                style={{
                  marginTop: "24px",
                  maxWidth: isMobile
                    ? "100%"
                    : "720px",
                  color: "#9b9b9b",
                  lineHeight: 1.7,
                  fontSize: isMobile
                    ? "1rem"
                    : "1.15rem",
                }}
              >
                Full Stack Engineer &
                AI Enthusiast.
                Building scalable AI
                systems, cloud-native
                apps, modern RAG
                applications, and
                impactful developer
                experiences.
              </p>

              {/* QUICK PROMPTS */}
              <div
                style={{
                  marginTop: "22px",
                  animation:
                    "fadeUp 1.4s ease 0.8s both",
                  marginBottom:
                    "80px",
                  display: "flex",
                  flexWrap: "wrap",
                  justifyContent:
                    isMobile
                      ? "center"
                      : "flex-start",
                  gap: isMobile
                    ? "10px"
                    : "14px",
                  position:
                    "relative",
                  zIndex: 10,
                }}
              >
                {quickPrompts.map(
                  (
                    prompt,
                    index
                  ) => (
                    <button
                      key={index}
                      onClick={() =>
                        askQuestion(
                          prompt
                        )
                      }
                      style={{
                        background:
                          "#101010",
                        border:
                          "1px solid #242424",
                        color: "white",
                        padding: isMobile
                          ? "10px 14px"
                          : "12px 18px",
                        borderRadius:
                          "999px",
                        cursor:
                          "pointer",
                        fontSize: isMobile
                          ? "0.82rem"
                          : "0.92rem",
                      }}
                    >
                      {prompt}
                    </button>
                  )
                )}
              </div>
            </div>

            {/* RIGHT */}
            <div
              style={{
                position: "relative",
                display: "flex",
                justifyContent:
                  "center",
                alignItems:
                  "center",
                marginTop: isMobile
                  ? "10px"
                  : "0",
                overflow: "visible",
                minHeight: isMobile
                  ? "480px"
                  : "650px",
              }}
            >
              <div
                style={{
                  width: isMobile
                    ? "250px"
                    : "520px",
                  height: isMobile
                    ? "250px"
                    : "520px",
                  borderRadius:
                    "50%",
                  background:
                    "#ffcc00",
                  position:
                    "absolute",
                  opacity: 1,
                  filter:
                    "drop-shadow(0 0 80px rgba(255,204,0,0.28))",
                }}
              />

              <img
                src={tushitImage}
                alt="Tushit"
                style={{
                  width: isMobile
                    ? "340px"
                    : "510px",
                  maxWidth: "100%",
                  objectFit:
                    "contain",
                  position:
                    "relative",
                  zIndex: 2,
                  top: isMobile
                    ? "30px"
                    : "-115px",
                  animation:
                    "fadeUp 1.2s ease 0.6s both, floating 4s ease-in-out infinite 1.8s",
                }}
              />
            </div>
          </div>
        ) : (
          <div
            ref={
              messagesContainerRef
            }
            style={{
              height:
                "calc(100vh - 140px)",
              overflowY: "auto",
              padding: isMobile
                ? "100px 14px 140px"
                : "120px 42px 170px 42px",
              display: "flex",
              flexDirection:
                "column",
              gap: "24px",
              scrollBehavior:
                "smooth",
            }}
          >
            {messages.map(
              (msg, index) => (
                <div
                  key={index}
                  style={{
                    display:
                      "flex",
                    justifyContent:
                      msg.type ===
                      "user"
                        ? "flex-end"
                        : "flex-start",
                  }}
                >
                  {msg.type ===
                  "user" ? (
                    <div
                      style={{
                        background:
                          "#ffcc00",
                        color:
                          "black",
                        padding:
                          "16px 22px",
                        borderRadius:
                          "22px 22px 6px 22px",
                        maxWidth: isMobile
                          ? "90%"
                          : "420px",
                        fontWeight: 600,
                        fontSize:
                          "1rem",
                      }}
                    >
                      {msg.text}
                    </div>
                  ) : (
                    <div
                      style={{
                        display:
                          "flex",
                        gap: "14px",
                        alignItems:
                          "flex-start",
                        maxWidth: isMobile
                          ? "100%"
                          : "900px",
                      }}
                    >
                      <img
                        src={
                          tushitImage
                        }
                        alt=""
                        style={{
                          width:
                            "44px",
                          height:
                            "44px",
                          borderRadius:
                            "50%",
                          objectFit:
                            "cover",
                          border:
                            "2px solid #ffcc00",
                          flexShrink: 0,
                        }}
                      />

                      <div
                        style={{
                          background:
                            "#111111",
                          border:
                            "1px solid #242424",
                          borderRadius:
                            "22px 22px 22px 6px",
                          padding: isMobile
                            ? "18px"
                            : "22px",
                          width:
                            "100%",
                        }}
                      >
                        <ReactMarkdown
                          components={{
                            p: ({
                              children,
                            }) => (
                              <p
                                style={{
                                  lineHeight: 1.9,
                                  marginBottom:
                                    "16px",
                                  color:
                                    "white",
                                  fontSize:
                                    isMobile
                                      ? "0.96rem"
                                      : "1rem",
                                }}
                              >
                                {
                                  children
                                }
                              </p>
                            ),

                            h1: ({
                              children,
                            }) => (
                              <h1
                                style={{
                                  color:
                                    "#ffcc00",
                                  fontSize:
                                    isMobile
                                      ? "1.4rem"
                                      : "1.7rem",
                                  marginBottom:
                                    "16px",
                                  marginTop:
                                    "10px",
                                  lineHeight: 1.3,
                                }}
                              >
                                {
                                  children
                                }
                              </h1>
                            ),

                            h2: ({
                              children,
                            }) => (
                              <h2
                                style={{
                                  color:
                                    "#ffcc00",
                                  fontSize:
                                    isMobile
                                      ? "1.2rem"
                                      : "1.45rem",
                                  marginBottom:
                                    "14px",
                                  marginTop:
                                    "10px",
                                  lineHeight: 1.3,
                                }}
                              >
                                {
                                  children
                                }
                              </h2>
                            ),

                            h3: ({
                              children,
                            }) => (
                              <h3
                                style={{
                                  color:
                                    "#ffcc00",
                                  fontSize:
                                    isMobile
                                      ? "1.05rem"
                                      : "1.2rem",
                                  marginBottom:
                                    "12px",
                                  lineHeight: 1.3,
                                }}
                              >
                                {
                                  children
                                }
                              </h3>
                            ),

                            ul: ({
                              children,
                            }) => (
                              <ul
                                style={{
                                  paddingLeft:
                                    "24px",
                                  marginBottom:
                                    "16px",
                                  lineHeight: 1.9,
                                }}
                              >
                                {
                                  children
                                }
                              </ul>
                            ),

                            ol: ({
                              children,
                            }) => (
                              <ol
                                style={{
                                  paddingLeft:
                                    "24px",
                                  marginBottom:
                                    "16px",
                                  lineHeight: 1.9,
                                }}
                              >
                                {
                                  children
                                }
                              </ol>
                            ),

                            li: ({
                              children,
                            }) => (
                              <li
                                style={{
                                  marginBottom:
                                    "8px",
                                }}
                              >
                                {
                                  children
                                }
                              </li>
                            ),

                            strong: ({
                              children,
                            }) => (
                              <strong
                                style={{
                                  color:
                                    "#ffcc00",
                                  fontWeight: 700,
                                }}
                              >
                                {
                                  children
                                }
                              </strong>
                            ),

                            code: ({
                              children,
                            }) => (
                              <code
                                style={{
                                  background:
                                    "#1a1a1a",
                                  padding:
                                    "3px 8px",
                                  borderRadius:
                                    "8px",
                                  color:
                                    "#ffcc00",
                                  fontSize:
                                    "0.92rem",
                                }}
                              >
                                {
                                  children
                                }
                              </code>
                            ),
                          }}
                        >
                          {msg.text}
                        </ReactMarkdown>
                      </div>
                    </div>
                  )}
                </div>
              )
            )}

            {loading && (
              <div
                style={{
                  display: "flex",
                  gap: "14px",
                  alignItems:
                    "center",
                }}
              >
                <img
                  src={tushitImage}
                  alt=""
                  style={{
                    width: "44px",
                    height:
                      "44px",
                    borderRadius:
                      "50%",
                    border:
                      "2px solid #ffcc00",
                  }}
                />

                <div
                  style={{
                    background:
                      "#111111",
                    border:
                      "1px solid #242424",
                    padding:
                      "18px 22px",
                    borderRadius:
                      "20px",
                  }}
                >
                  Thinking...
                </div>
              </div>
            )}
          </div>
        )}

        {/* INPUT BAR */}
        <div
          style={{
            position: "fixed",
            bottom: isMobile
              ? "14px"
              : "24px",
            left: "50%",
            transform:
              "translateX(-50%)",
            width:
              "min(1200px, 92%)",
            background:
              "rgba(16,16,16,0.95)",
            border:
              "1px solid #242424",
            borderRadius: "30px",
            padding: isMobile
              ? "14px"
              : "18px",
            backdropFilter:
              "blur(14px)",
            zIndex: 999,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems:
                "center",
              gap: "14px",
            }}
          >
            <input
              type="text"
              value={query}
              onChange={(e) =>
                setQuery(
                  e.target.value
                )
              }
              onKeyDown={(e) => {
                if (
                  e.key ===
                  "Enter"
                ) {
                  askQuestion();
                }
              }}
              placeholder="Ask about my projects, experience, AI systems, DevOps..."
              style={{
                flex: 1,
                background:
                  "transparent",
                border: "none",
                outline: "none",
                color: "white",
                fontSize: isMobile
                  ? "0.95rem"
                  : "1.1rem",
              }}
            />

            <button
              onClick={() =>
                askQuestion()
              }
              style={{
                width: isMobile
                  ? "52px"
                  : "62px",
                height: isMobile
                  ? "52px"
                  : "62px",
                borderRadius:
                  "18px",
                border: "none",
                background:
                  "#ffcc00",
                color: "black",
                cursor:
                  "pointer",
                display: "flex",
                alignItems:
                  "center",
                justifyContent:
                  "center",
                fontSize: "1.3rem",
                flexShrink: 0,
              }}
            >
              <FaArrowUp />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

const iconStyle = {
  width: "58px",
  height: "58px",
  borderRadius: "50%",
  border:
    "1px solid #2a2a2a",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  color: "white",
  textDecoration: "none",
  fontSize: "1.2rem",
  background: "#090909",
};

export default App;