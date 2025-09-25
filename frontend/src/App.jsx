import {
  Box,
  Container,
  VStack,
  Heading,
  Text,
  HStack,
  Icon,
  Card,
} from "@chakra-ui/react";
import { Sprout } from "lucide-react";
import ChatInterface from "./components/ChatInterface";

function App() {
  return (
    <Box minH="100vh" bg="linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
      <Container maxW="container.xl" py="4">
        <VStack spacing="6" h="100vh">
          {/* Header */}
          <Card.Root w="full" variant="elevated" bg="white" shadow="lg">
            <Card.Body py="4">
              <HStack justify="center" spacing="3">
                <Box p="2" bg="primary.500" borderRadius="lg" color="white">
                  <Icon boxSize="8">
                    <Sprout />
                  </Icon>
                </Box>
                <VStack spacing="1" align="center">
                  <Heading size="lg" color="primary.700" fontWeight="bold">
                    農業天気アドバイザー
                  </Heading>
                  <Text color="gray.600" fontSize="sm">
                    Agricultural Weather Advisor
                  </Text>
                  <Text color="primary.600" fontSize="xs" fontWeight="medium">
                    🎤 音声入力対応 | Voice Input Supported
                  </Text>
                </VStack>
              </HStack>
            </Card.Body>
          </Card.Root>

          {/* Main Chat Interface */}
          <Box flex="1" w="full">
            <ChatInterface />
          </Box>
        </VStack>
      </Container>
    </Box>
  );
}

export default App;
