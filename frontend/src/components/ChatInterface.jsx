// import { useState, useRef, useEffect } from "react";
// import {
//   Box,
//   VStack,
//   HStack,
//   Button,
//   Input,
//   Text,
//   Card,
//   Icon,
//   Alert,
//   Badge,
//   Spinner,
// } from "@chakra-ui/react";
// import {
//   Mic,
//   MicOff,
//   Send,
//   MessageCircle,
//   MapPin,
//   Thermometer,
//   Brain,
// } from "lucide-react";
// import { useVoiceRecognition } from "../hooks/useVoiceRecognition";
// import { chatAPI, weatherAPI } from "../services/api";

// function ChatInterface() {
//   // State management
//   const [messages, setMessages] = useState([]);
//   const [inputText, setInputText] = useState("");
//   const [isLoading, setIsLoading] = useState(false);
//   const [currentWeather, setCurrentWeather] = useState(null);
//   const [error, setError] = useState(null);
//   const [sessionId, setSessionId] = useState(null);
//   const [currentLocation, setCurrentLocation] = useState({
//     city: "Tokyo",
//     country: "JP",
//   });

//   // Voice recognition
//   const {
//     isListening,
//     transcript,
//     isSupported,
//     error: voiceError,
//     startListening,
//     stopListening,
//     resetTranscript,
//   } = useVoiceRecognition();

//   const messagesEndRef = useRef(null);

//   // Auto-scroll to bottom
//   useEffect(() => {
//     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
//   }, [messages]);

//   // Load initial weather and welcome message
//   useEffect(() => {
//     loadInitialData();
//   }, []);

//   // Handle voice transcript completion
//   useEffect(() => {
//     if (!isListening && transcript.trim()) {
//       handleSendMessage(transcript);
//       resetTranscript();
//     }
//   }, [isListening, transcript]);

//   const loadInitialData = async () => {
//     try {
//       // Load weather data for default location
//       const weatherData = await weatherAPI.getCurrentWeather("Tokyo", "JP");
//       setCurrentWeather(weatherData);

//       // Add welcome message
//       const welcomeMessage = {
//         id: Date.now(),
//         type: "system",
//         content: {
//           japanese:
//             "🌾 こんにちは！農業天気アドバイザーです。「東京の天気はどう？」や「ムンバイの農業について教えて」など、場所を含めて質問してください。",
//           english:
//             '🌾 Hello! I am your Agricultural Weather Advisor. Ask questions like "How\'s the weather in Tokyo?" or "Tell me about farming in Mumbai" - I can understand locations from your messages!',
//         },
//         timestamp: new Date(),
//       };
//       setMessages([welcomeMessage]);
//     } catch (err) {
//       console.error("Failed to load initial data:", err);
//     }
//   };

//   const handleSendMessage = async (message) => {
//     const text = message || inputText.trim();
//     if (!text) return;

//     setIsLoading(true);
//     setError(null);

//     // Add user message
//     const userMessage = {
//       id: Date.now(),
//       type: "user",
//       content: text,
//       timestamp: new Date(),
//     };
//     setMessages((prev) => [...prev, userMessage]);
//     setInputText("");

//     try {
//       // Send to enhanced backend with session management
//       const response = await chatAPI.sendMessage({
//         message: text,
//         session_id: sessionId,
//         language: "japanese",
//       });

//       if (response.success) {
//         // Update session ID if new
//         if (response.session_id && response.session_id !== sessionId) {
//           setSessionId(response.session_id);
//         }

//         // Check if location was extracted/changed
//         const locationInfo = response.location_info;
//         if (locationInfo && locationInfo.location_changed) {
//           setCurrentLocation(locationInfo.current_location);

//           // Add location change notification
//           const locationChangeMessage = {
//             id: Date.now() + 0.5,
//             type: "location_change",
//             content: {
//               japanese: `📍 位置が${locationInfo.current_location.city}, ${locationInfo.current_location.country}に変更されました。この場所の天気と農業情報を取得しています。`,
//               english: `📍 Location changed to ${locationInfo.current_location.city}, ${locationInfo.current_location.country}. Getting weather and agricultural info for this location.`,
//             },
//             location_data: locationInfo.extracted_location,
//             timestamp: new Date(),
//           };
//           setMessages((prev) => [...prev, locationChangeMessage]);
//         }

//         // Add AI response
//         const aiMessage = {
//           id: Date.now() + 1,
//           type: "assistant",
//           content: {
//             japanese: response.response,
//             english: response.response, // Backend provides integrated response
//           },
//           weather: response.weather,
//           recommendations: response.crop_recommendations,
//           location: locationInfo
//             ? locationInfo.current_location
//             : currentLocation,
//           confidence: locationInfo ? locationInfo.confidence : 0,
//           timestamp: new Date(),
//         };
//         setMessages((prev) => [...prev, aiMessage]);

//         // Update weather if provided
//         if (response.weather) {
//           setCurrentWeather(response.weather);
//         }
//       }
//     } catch (err) {
//       setError(err.message);

//       // Add error message
//       const errorMessage = {
//         id: Date.now() + 1,
//         type: "error",
//         content: {
//           japanese: `エラーが発生しました: ${err.message}`,
//           english: `Error occurred: ${err.message}`,
//         },
//         timestamp: new Date(),
//       };
//       setMessages((prev) => [...prev, errorMessage]);
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleVoiceToggle = () => {
//     if (isListening) {
//       stopListening();
//     } else {
//       startListening();
//     }
//   };

//   return (
//     <VStack spacing="4" h="full">
//       {/* Current Location & Weather Display */}
//       <Card.Root w="full" variant="subtle" bg="white/90" backdrop="blur(10px)">
//         <Card.Body py="3">
//           <HStack justify="space-between" align="center">
//             <HStack spacing="3">
//               <Icon color="blue.500">
//                 <MapPin />
//               </Icon>
//               <VStack align="start" spacing="0">
//                 <HStack spacing="2">
//                   <Text fontSize="sm" fontWeight="semibold">
//                     📍{" "}
//                     {currentWeather?.data?.location ||
//                       `${currentLocation.city}, ${currentLocation.country}`}
//                   </Text>
//                   <Badge size="sm" colorScheme="green" variant="subtle">
//                     <Icon boxSize="3" mr="1">
//                       <Brain />
//                     </Icon>
//                     AI Location
//                   </Badge>
//                 </HStack>
//                 <Text fontSize="xs" color="gray.600">
//                   {currentWeather?.data?.description || "Clear sky"} • Just
//                   mention a city in your message!
//                 </Text>
//               </VStack>
//             </HStack>

//             <HStack spacing="4">
//               <HStack spacing="1">
//                 <Icon color="orange.500">
//                   <Thermometer />
//                 </Icon>
//                 <Text fontSize="lg" fontWeight="bold" color="primary.600">
//                   {currentWeather?.data?.temperature || "25"}°C
//                 </Text>
//               </HStack>
//               <Badge colorScheme="blue" variant="subtle">
//                 Live Weather
//               </Badge>
//             </HStack>
//           </HStack>
//         </Card.Body>
//       </Card.Root>

//       {/* Messages Area */}
//       <Box
//         flex="1"
//         w="full"
//         overflowY="auto"
//         p="4"
//         bg="white/80"
//         borderRadius="xl"
//         backdropFilter="blur(10px)"
//         border="1px solid"
//         borderColor="white/30"
//       >
//         <VStack spacing="4" align="stretch">
//           {messages.map((message) => (
//             <MessageBubble key={message.id} message={message} />
//           ))}

//           {/* Voice transcript preview */}
//           {isListening && transcript && (
//             <Box
//               alignSelf="flex-end"
//               bg="blue.100"
//               p="3"
//               borderRadius="lg"
//               border="2px dashed"
//               borderColor="blue.300"
//               maxW="80%"
//             >
//               <HStack>
//                 <Spinner size="sm" color="blue.500" />
//                 <Text fontSize="sm" color="blue.700" fontStyle="italic">
//                   🎤 "{transcript}..."
//                 </Text>
//               </HStack>
//             </Box>
//           )}

//           {/* Loading indicator */}
//           {isLoading && (
//             <Box alignSelf="flex-start" maxW="80%">
//               <Card.Root variant="subtle">
//                 <Card.Body py="3">
//                   <HStack>
//                     <Spinner size="sm" color="primary.500" />
//                     <Text fontSize="sm" color="gray.600">
//                       🧠 AI analyzing your message for location and weather
//                       context...
//                     </Text>
//                   </HStack>
//                 </Card.Body>
//               </Card.Root>
//             </Box>
//           )}

//           <div ref={messagesEndRef} />
//         </VStack>
//       </Box>

//       {/* Error Display */}
//       {(error || voiceError) && (
//         <Alert.Root status="error" w="full">
//           <Alert.Icon />
//           <Alert.Description>{error || voiceError}</Alert.Description>
//         </Alert.Root>
//       )}

//       {/* Input Area */}
//       <Card.Root w="full" variant="elevated" bg="white" shadow="xl">
//         <Card.Body>
//           <VStack spacing="3">
//             {/* Example prompts */}
//             <Box w="full" textAlign="center">
//               <Text fontSize="xs" color="gray.500" mb="2">
//                 💡 Try: "How's farming in Mumbai?" • "Tell me about Tokyo
//                 weather" • "Agriculture in London"
//               </Text>
//             </Box>

//             {/* Voice Input Button */}
//             {isSupported && (
//               <HStack justify="center" w="full">
//                 <Button
//                   onClick={handleVoiceToggle}
//                   colorScheme={isListening ? "red" : "primary"}
//                   size="lg"
//                   leftIcon={isListening ? <MicOff /> : <Mic />}
//                   isLoading={isListening}
//                   loadingText="音声認識中..."
//                   borderRadius="full"
//                   px="8"
//                   _hover={{ transform: "scale(1.05)" }}
//                   transition="all 0.2s"
//                 >
//                   {isListening
//                     ? "停止 / Stop"
//                     : "🎤 場所を含めて話す / Speak with location"}
//                 </Button>
//               </HStack>
//             )}

//             {/* Text Input */}
//             <HStack spacing="2" w="full">
//               <Input
//                 value={inputText}
//                 onChange={(e) => setInputText(e.target.value)}
//                 onKeyPress={(e) =>
//                   e.key === "Enter" && !e.shiftKey && handleSendMessage()
//                 }
//                 placeholder={
//                   isListening
//                     ? "音声入力中... / Voice input active..."
//                     : "Ask about farming in any city... / どの都市の農業についても質問できます..."
//                 }
//                 size="lg"
//                 borderRadius="full"
//                 bg="gray.50"
//                 border="2px solid"
//                 borderColor="gray.200"
//                 _focus={{
//                   borderColor: "primary.400",
//                   boxShadow: "0 0 0 1px var(--chakra-colors-primary-400)",
//                 }}
//                 isDisabled={isListening || isLoading}
//               />
//               <Button
//                 onClick={() => handleSendMessage()}
//                 colorScheme="primary"
//                 size="lg"
//                 borderRadius="full"
//                 leftIcon={<Send />}
//                 isDisabled={!inputText.trim() || isListening || isLoading}
//               >
//                 送信
//               </Button>
//             </HStack>
//           </VStack>
//         </Card.Body>
//       </Card.Root>
//     </VStack>
//   );
// }

// // Enhanced Message Bubble Component
// function MessageBubble({ message }) {
//   const { type, content, timestamp, location, confidence, location_data } =
//     message;

//   const getBubbleStyles = () => {
//     switch (type) {
//       case "user":
//         return {
//           alignSelf: "flex-end",
//           bg: "primary.500",
//           color: "white",
//           maxW: "80%",
//         };
//       case "system":
//         return {
//           alignSelf: "center",
//           bg: "blue.100",
//           color: "blue.800",
//           maxW: "90%",
//         };
//       case "location_change":
//         return {
//           alignSelf: "center",
//           bg: "green.100",
//           color: "green.800",
//           maxW: "90%",
//         };
//       case "error":
//         return {
//           alignSelf: "center",
//           bg: "red.100",
//           color: "red.800",
//           maxW: "90%",
//         };
//       default:
//         return {
//           alignSelf: "flex-start",
//           bg: "white",
//           color: "gray.800",
//           maxW: "85%",
//           shadow: "md",
//         };
//     }
//   };

//   const bubbleStyles = getBubbleStyles();

//   return (
//     <Box {...bubbleStyles}>
//       <Card.Root
//         variant="outline"
//         bg={bubbleStyles.bg}
//         color={bubbleStyles.color}
//       >
//         <Card.Body p="4">
//           <VStack spacing="2" align="stretch">
//             {/* Location badge and confidence for assistant messages */}
//             {type === "assistant" && location && (
//               <HStack justify="space-between">
//                 <HStack>
//                   <Badge size="sm" colorScheme="green" variant="subtle">
//                     📍 {location.city}, {location.country}
//                   </Badge>
//                   {confidence > 0 && (
//                     <Badge
//                       size="sm"
//                       colorScheme={
//                         confidence > 0.8
//                           ? "blue"
//                           : confidence > 0.6
//                           ? "yellow"
//                           : "gray"
//                       }
//                       variant="subtle"
//                     >
//                       🧠 {Math.round(confidence * 100)}%
//                     </Badge>
//                   )}
//                 </HStack>
//                 <Text fontSize="xs" opacity="0.6">
//                   {new Date(timestamp).toLocaleTimeString("ja-JP", {
//                     hour: "2-digit",
//                     minute: "2-digit",
//                   })}
//                 </Text>
//               </HStack>
//             )}

//             {/* Location extraction info for location change messages */}
//             {type === "location_change" && location_data && (
//               <HStack justify="center" mb="2">
//                 <Badge colorScheme="green" size="sm">
//                   🎯 Extracted: "{location_data.extracted_phrase}" (Confidence:{" "}
//                   {Math.round(location_data.confidence * 100)}%)
//                 </Badge>
//               </HStack>
//             )}

//             {/* Message Content */}
//             {typeof content === "string" ? (
//               <Text fontSize="md" lineHeight="1.6">
//                 {content}
//               </Text>
//             ) : (
//               <VStack spacing="2" align="stretch">
//                 {/* Japanese */}
//                 <Box>
//                   <Text fontSize="xs" opacity="0.7" mb="1">
//                     🇯🇵 日本語
//                   </Text>
//                   <Text fontSize="md" lineHeight="1.6" fontFamily="heading">
//                     {content.japanese}
//                   </Text>
//                 </Box>

//                 {/* English */}
//                 {content.english && content.english !== content.japanese && (
//                   <Box pt="2" borderTop="1px solid" borderColor="gray.200">
//                     <Text fontSize="xs" opacity="0.7" mb="1">
//                       🇺🇸 English
//                     </Text>
//                     <Text fontSize="sm" lineHeight="1.5" opacity="0.8">
//                       {content.english}
//                     </Text>
//                   </Box>
//                 )}
//               </VStack>
//             )}

//             {/* Timestamp for user/error messages */}
//             {(type === "user" || type === "error" || type === "system") && (
//               <Text fontSize="xs" opacity="0.6" textAlign="right">
//                 {new Date(timestamp).toLocaleTimeString("ja-JP", {
//                   hour: "2-digit",
//                   minute: "2-digit",
//                 })}
//               </Text>
//             )}
//           </VStack>
//         </Card.Body>
//       </Card.Root>
//     </Box>
//   );
// }

// export default ChatInterface;




import { useState, useRef, useEffect } from "react";
import {
  Box,
  VStack,
  HStack,
  Button,
  Input,
  Text,
  Spinner,
  Badge,
} from "@chakra-ui/react";
import {
  Mic,
  MicOff,
  Send,
  MapPin,
  Thermometer,
  Brain,
  Square,
} from "lucide-react";
import { useDeepgramVoiceRecording } from "../hooks/useDeepgramVoiceRecording";
import { chatAPI, weatherAPI } from "../services/api";

function ChatInterface() {
  // State management
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [currentWeather, setCurrentWeather] = useState(null);
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [currentLocation, setCurrentLocation] = useState({
    city: "Tokyo",
    country: "JP",
  });

  // Deepgram voice recording
  const {
    isRecording,
    isProcessing,
    transcript,
    confidence,
    error: voiceError,
    isSupported,
    startRecording,
    stopRecording,
    // resetTranscript,
  } = useDeepgramVoiceRecording();

  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Load initial weather and welcome message
  useEffect(() => {
    loadInitialData();
  }, []);

  // Show voice errors in error state
  useEffect(() => {
    if (voiceError) {
      setError(voiceError);
    }
  }, [voiceError]);

  // Set up global handler for voice processing results
  useEffect(() => {
    window.deepgramResult = handleVoiceProcessingResult;
    return () => {
      delete window.deepgramResult;
    };
  }, [sessionId, currentLocation]);

  const loadInitialData = async () => {
    try {
      // Load weather data for default location
      const weatherData = await weatherAPI.getCurrentWeather("Tokyo", "JP");
      setCurrentWeather(weatherData);

      // Add welcome message
      const welcomeMessage = {
        id: Date.now(),
        type: "system",
        content: {
          japanese:
            "🌾 こんにちは！農業天気アドバイザーです。音声入力（Deepgram AI搭載）やテキストで質問してください。「東京の天気はどう？」「ムンバイの農業について教えて」などの場所を含む質問が得意です。",
          english:
            '🌾 Hello! I am your Agricultural Weather Advisor with Deepgram AI-powered voice input. Ask questions using voice or text like "How\'s the weather in Tokyo?" or "Tell me about farming in Mumbai"!',
        },
        timestamp: new Date(),
      };
      setMessages([welcomeMessage]);
    } catch (err) {
      console.error("Failed to load initial data:", err);
      setError("アプリケーションの初期化に失敗しました");
    }
  };

  const handleSendMessage = async (message) => {
    const text = message || inputText.trim();
    if (!text) return;

    setIsLoading(true);
    setError(null);

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: "user",
      content: text,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputText("");

    try {
      // Send to enhanced backend with session management
      const response = await chatAPI.sendMessage({
        message: text,
        session_id: sessionId,
        language: "japanese",
      });

      processIntelligentChatResponse(response);

    } catch (err) {
      setError(err.message);

      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        type: "error",
        content: {
          japanese: `エラーが発生しました: ${err.message}`,
          english: `Error occurred: ${err.message}`,
        },
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceProcessingResult = (voiceResult) => {
    console.log("🎯 Processing voice result:", voiceResult);
    
    if (!voiceResult.success) {
      setError(voiceResult.error || "音声処理に失敗しました");
      return;
    }

    // Add user message with voice metadata
    const userMessage = {
      id: Date.now(),
      type: "user",
      content: voiceResult.transcription.transcript,
      voice_metadata: {
        confidence: voiceResult.transcription.confidence,
        processing_time: voiceResult.transcription.processing_time,
        word_count: voiceResult.transcription.word_count,
      },
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Show low confidence warning in console
    if (voiceResult.transcription.confidence < 0.7) {
      console.warn(`Low transcription confidence: ${Math.round(voiceResult.transcription.confidence * 100)}%`);
    }

    // Process the chat response
    const chatResponse = {
      success: voiceResult.chat_response.success,
      response: voiceResult.chat_response.response,
      session_id: voiceResult.session_id,
      location_info: voiceResult.location_info,
      weather: voiceResult.weather,
      crop_recommendations: voiceResult.crop_recommendations,
      query_intelligence: voiceResult.query_intelligence
    };

    processIntelligentChatResponse(chatResponse, true);
  };

  const processIntelligentChatResponse = (response, isVoiceInput = false) => {
    if (response.success) {
      // Update session ID if new
      if (response.session_id && response.session_id !== sessionId) {
        setSessionId(response.session_id);
      }

      // Check if location was extracted/changed
      const locationInfo = response.location_info;
      if (locationInfo && locationInfo.location_changed) {
        setCurrentLocation(locationInfo.current_location);

        // Add location change notification
        const locationChangeMessage = {
          id: Date.now() + 0.5,
          type: "location_change",
          content: {
            japanese: `📍 位置が${locationInfo.current_location.city}, ${locationInfo.current_location.country}に変更されました。この場所の天気と農業情報を取得しています。`,
            english: `📍 Location changed to ${locationInfo.current_location.city}, ${locationInfo.current_location.country}. Getting weather and agricultural info for this location.`,
          },
          location_data: locationInfo.extracted_location,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, locationChangeMessage]);
      }

      // Add AI response
      const aiMessage = {
        id: Date.now() + 1,
        type: "assistant",
        content: {
          japanese: response.response,
          english: response.response,
        },
        weather: response.weather,
        recommendations: response.crop_recommendations,
        location: locationInfo
          ? locationInfo.current_location
          : currentLocation,
        confidence: locationInfo ? locationInfo.confidence : 0,
        query_intelligence: response.query_intelligence,
        voice_input: isVoiceInput,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);

      // Update weather if provided
      if (response.weather) {
        setCurrentWeather(response.weather);
      }

      // Show query intelligence info for voice inputs in console
      if (isVoiceInput && response.query_intelligence) {
        const queryType = response.query_intelligence.classification.query_type;
        console.log(`Voice query analyzed: ${queryType}`);
      }
    }
  };

  const handleVoiceToggle = async () => {
    if (isRecording) {
      stopRecording();
    } else if (isProcessing) {
      console.log("Voice processing cancelled");
    } else {
      await startRecording();
    }
  };

  const getVoiceButtonState = () => {
    if (isProcessing) {
      return {
        text: "AI転写中... / AI Transcribing...",
        colorScheme: "yellow",
        icon: <Spinner size="sm" />,
        isLoading: true,
      };
    }
    
    if (isRecording) {
      return {
        text: "停止 / Stop Recording",
        colorScheme: "red",
        icon: <Square size={16} />,
        isLoading: false,
      };
    }
    
    return {
      text: "🎤 Deepgram AIで話す / Speak with AI",
      colorScheme: "blue",
      icon: <Mic size={16} />,
      isLoading: false,
    };
  };

  const voiceButtonState = getVoiceButtonState();

  return (
    <VStack spacing="4" h="full">
      {/* Current Location & Weather Display */}
      <Box w="full" p="3" bg="white" borderRadius="lg" shadow="sm" border="1px solid" borderColor="gray.200">
        <HStack justify="space-between" align="center">
          <HStack spacing="3">
            <MapPin size={20} color="blue" />
            <VStack align="start" spacing="0">
              <HStack spacing="2">
                <Text fontSize="sm" fontWeight="semibold">
                  📍{" "}
                  {currentWeather?.data?.location ||
                    `${currentLocation.city}, ${currentLocation.country}`}
                </Text>
                <Badge size="sm" colorScheme="green" variant="subtle">
                  <HStack spacing="1">
                    <Brain size={12} />
                    <Text>AI Location</Text>
                  </HStack>
                </Badge>
              </HStack>
              <Text fontSize="xs" color="gray.600">
                {currentWeather?.data?.description || "Clear sky"} • Powered by Deepgram AI Voice Recognition
              </Text>
            </VStack>
          </HStack>

          <HStack spacing="4">
            <HStack spacing="1">
              <Thermometer size={16} color="orange" />
              <Text fontSize="lg" fontWeight="bold" color="blue.600">
                {currentWeather?.data?.temperature || "25"}°C
              </Text>
            </HStack>
            <Badge colorScheme="blue" variant="subtle">
              Live Weather
            </Badge>
          </HStack>
        </HStack>
      </Box>

      {/* Messages Area */}
      <Box
        flex="1"
        w="full"
        overflowY="auto"
        p="4"
        bg="gray.50"
        borderRadius="xl"
        border="1px solid"
        borderColor="gray.200"
      >
        <VStack spacing="4" align="stretch">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}

          {/* Voice recording status */}
          {(isRecording || isProcessing) && (
            <Box
              alignSelf="flex-end"
              bg={isProcessing ? "yellow.100" : "blue.100"}
              p="3"
              borderRadius="lg"
              border="2px dashed"
              borderColor={isProcessing ? "yellow.300" : "blue.300"}
              maxW="80%"
            >
              <VStack spacing={2}>
                <HStack>
                  <Spinner size="sm" color={isProcessing ? "yellow.500" : "blue.500"} />
                  <Text fontSize="sm" color={isProcessing ? "yellow.700" : "blue.700"} fontWeight="medium">
                    {isProcessing ? 
                      "🤖 Deepgram AIで音声を解析中..." : 
                      "🎤 録音中... 話してください"}
                  </Text>
                </HStack>
                
                {transcript && (
                  <Text fontSize="sm" color="gray.600" fontStyle="italic">
                    "{transcript}" {confidence > 0 && `(${Math.round(confidence * 100)}%)`}
                  </Text>
                )}
              </VStack>
            </Box>
          )}

          {/* Loading indicator */}
          {isLoading && (
            <Box alignSelf="flex-start" maxW="80%">
              <Box variant="outline" p="3" bg="white" borderRadius="lg" border="1px solid" borderColor="gray.200">
                <HStack>
                  <Spinner size="sm" color="blue.500" />
                  <Text fontSize="sm" color="gray.600">
                    🧠 AIが位置情報と天気を分析しています...
                  </Text>
                </HStack>
              </Box>
            </Box>
          )}

          <div ref={messagesEndRef} />
        </VStack>
      </Box>

      {/* Error Display */}
      {error && (
        <Box w="full" p="3" bg="red.100" borderRadius="md" border="1px solid" borderColor="red.200">
          <Text color="red.800" fontSize="sm">{error}</Text>
        </Box>
      )}

      {/* Input Area */}
      <Box w="full" p="4" bg="white" borderRadius="xl" shadow="lg" border="1px solid" borderColor="gray.200">
        <VStack spacing="3">
          {/* Example prompts */}
          <Box w="full" textAlign="center">
            <Text fontSize="xs" color="gray.500" mb="2">
              💡 Try: "How's farming in Mumbai?" • "Tell me about Tokyo weather" • "Agriculture in London"
            </Text>
          </Box>

          {/* Voice Input Button */}
          {isSupported && (
            <HStack justify="center" w="full">
              <Button
                onClick={handleVoiceToggle}
                colorScheme={voiceButtonState.colorScheme}
                size="lg"
                leftIcon={voiceButtonState.icon}
                isLoading={voiceButtonState.isLoading}
                borderRadius="full"
                px="8"
                _hover={{ transform: isRecording ? "none" : "scale(1.05)" }}
                transition="all 0.2s"
                isDisabled={isLoading}
              >
                {voiceButtonState.text}
              </Button>
            </HStack>
          )}

          {/* Voice system not supported message */}
          {!isSupported && (
            <Box textAlign="center" p="3" bg="orange.100" borderRadius="md">
              <Text fontSize="sm" color="orange.800">
                🎤 音声録音がサポートされていません。テキスト入力をお使いください。
              </Text>
            </Box>
          )}

          {/* Text Input */}
          <HStack spacing="2" w="full">
            <Input
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) =>
                e.key === "Enter" && !e.shiftKey && handleSendMessage()
              }
              placeholder={
                isRecording || isProcessing
                  ? "音声入力中... / Voice input active..."
                  : "Ask about farming in any city... / どの都市の農業についても質問できます..."
              }
              size="lg"
              borderRadius="full"
              bg="gray.50"
              border="2px solid"
              borderColor="gray.200"
              _focus={{
                borderColor: "blue.400",
                boxShadow: "0 0 0 1px var(--chakra-colors-blue-400)",
              }}
              isDisabled={isRecording || isProcessing || isLoading}
            />
            <Button
              onClick={() => handleSendMessage()}
              colorScheme="blue"
              size="lg"
              borderRadius="full"
              leftIcon={<Send size={16} />}
              isDisabled={!inputText.trim() || isRecording || isProcessing || isLoading}
            >
              送信
            </Button>
          </HStack>
        </VStack>
      </Box>
    </VStack>
  );
}

// Enhanced Message Bubble Component with Voice Metadata
function MessageBubble({ message }) {
  const { type, content, timestamp, location, confidence, location_data, voice_metadata, query_intelligence, voice_input } =
    message;

  const getBubbleStyles = () => {
    switch (type) {
      case "user":
        return {
          alignSelf: "flex-end",
          bg: voice_input ? "purple.500" : "blue.500", // Different color for voice inputs
          color: "white",
          maxW: "80%",
        };
      case "system":
        return {
          alignSelf: "center",
          bg: "blue.100",
          color: "blue.800",
          maxW: "90%",
        };
      case "location_change":
        return {
          alignSelf: "center",
          bg: "green.100",
          color: "green.800",
          maxW: "90%",
        };
      case "error":
        return {
          alignSelf: "center",
          bg: "red.100",
          color: "red.800",
          maxW: "90%",
        };
      default:
        return {
          alignSelf: "flex-start",
          bg: "white",
          color: "gray.800",
          maxW: "85%",
          shadow: "md",
        };
    }
  };

  const bubbleStyles = getBubbleStyles();

  return (
    <Box {...bubbleStyles}>
      <Box bg={bubbleStyles.bg} color={bubbleStyles.color} p="4" borderRadius="lg" border="1px solid" borderColor="gray.200">
        <VStack spacing="2" align="stretch">
          {/* Voice input metadata for user messages */}
          {type === "user" && voice_metadata && (
            <HStack justify="space-between" mb="1">
              <HStack spacing="1">
                <Mic size={12} />
                <Badge size="xs" colorScheme="purple" variant="solid">
                  🎤 Deepgram AI
                </Badge>
                <Badge size="xs" colorScheme="green" variant="solid">
                  {Math.round(voice_metadata.confidence * 100)}%
                </Badge>
              </HStack>
              <Text fontSize="xs" opacity={0.8}>
                {voice_metadata.word_count} words • {voice_metadata.processing_time}ms
              </Text>
            </HStack>
          )}

          {/* Location badge and confidence for assistant messages */}
          {type === "assistant" && location && (
            <HStack justify="space-between">
              <HStack>
                <Badge size="sm" colorScheme="green" variant="subtle">
                  📍 {location.city}, {location.country}
                </Badge>
                {confidence > 0 && (
                  <Badge
                    size="sm"
                    colorScheme={
                      confidence > 0.8 ? "blue" : confidence > 0.6 ? "yellow" : "gray"
                    }
                    variant="subtle"
                  >
                    🧠 {Math.round(confidence * 100)}%
                  </Badge>
                )}
                {query_intelligence && (
                  <Badge size="sm" colorScheme="purple" variant="subtle">
                    📊 {query_intelligence.classification.query_type}
                  </Badge>
                )}
              </HStack>
              <Text fontSize="xs" opacity={0.6}>
                {new Date(timestamp).toLocaleTimeString("ja-JP", {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </Text>
            </HStack>
          )}

          {/* Location extraction info for location change messages */}
          {type === "location_change" && location_data && (
            <HStack justify="center" mb="2">
              <Badge colorScheme="green" size="sm">
                🎯 Extracted: "{location_data.extracted_phrase}" (Confidence:{" "}
                {Math.round(location_data.confidence * 100)}%)
              </Badge>
            </HStack>
          )}

          {/* Message Content */}
          {typeof content === "string" ? (
            <Text fontSize="md" lineHeight="1.6">
              {content}
            </Text>
          ) : (
            <VStack spacing="2" align="stretch">
              {/* Japanese */}
              <Box>
                <Text fontSize="xs" opacity="0.7" mb="1">
                  🇯🇵 日本語
                </Text>
                <Text fontSize="md" lineHeight="1.6" fontFamily="heading">
                  {content.japanese}
                </Text>
              </Box>

              {/* English */}
              {content.english && content.english !== content.japanese && (
                <Box pt="2" borderTop="1px solid" borderColor="gray.200">
                  <Text fontSize="xs" opacity="0.7" mb="1">
                    🇺🇸 English
                  </Text>
                  <Text fontSize="sm" lineHeight="1.5" opacity="0.8">
                    {content.english}
                  </Text>
                </Box>
              )}
            </VStack>
          )}

          {/* Timestamp for other message types */}
          {(type === "user" || type === "error" || type === "system") && !voice_metadata && (
            <Text fontSize="xs" opacity={0.6} textAlign="right">
              {new Date(timestamp).toLocaleTimeString("ja-JP", {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </Text>
          )}
        </VStack>
      </Box>
    </Box>
  );
}

export default ChatInterface;