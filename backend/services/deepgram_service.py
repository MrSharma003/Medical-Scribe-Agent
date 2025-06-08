from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
from config.settings import Config

class DeepgramService:
    def __init__(self):
        self.client = DeepgramClient(Config.DEEPGRAM_API_KEY)
        
        # Streaming options for real-time transcription
        self.streaming_options = LiveOptions(
            model="nova-2",
            language="en-US",
            smart_format=True,
            punctuate=True,
            diarize=True,  # Enable speaker diarization
            multichannel=False,
            numerals=True,
            search=["medical", "healthcare", "patient", "doctor"],
            keywords=["patient", "doctor", "nurse", "provider"],
            interim_results=False,  # Disable interim for better speaker detection
            encoding="linear16",
            sample_rate=48000,
            channels=1,
        )
        
        # Store streaming connections per session
        self.connections = {}
        self.connection_transcripts = {}
        self.session_speaker_count = {}  # Track number of speakers per session

    def start_streaming_session(self, session_id: str, on_transcript_callback) -> bool:
        """Start a streaming session for real-time transcription"""
        try:
            print(f"Starting streaming session: {session_id}")
            
            # Create a live transcription connection using the correct pattern
            print("Creating live connection...")
            connection = self.client.listen.live.v("1")
            print("Live connection created successfully")
            
            # Store connection and initialize transcript buffer
            self.connections[session_id] = connection
            self.connection_transcripts[session_id] = ""
            self.session_speaker_count[session_id] = 1  # Start with speaker 1
            
            # Simple speaker inference state
            last_speaker_time = 0
            current_speaker = 1
            
            # Define event handler functions
            def on_open(connection_self, **kwargs):
                print(f"Streaming connection opened for session: {session_id}")
            
            def on_message(connection_self, result, **kwargs):
                sentence = result.channel.alternatives[0].transcript
                if sentence.strip():
                    # Extract speaker information if available
                    speaker_id = None
                    
                    # Debug: Print the structure to understand how Deepgram sends speaker info
                    print(f"Deepgram result structure: {type(result)}")
                    print(f"Has channel: {hasattr(result, 'channel')}")
                    if hasattr(result, 'channel'):
                        print(f"Channel type: {type(result.channel)}")
                        print(f"Has alternatives: {hasattr(result.channel, 'alternatives')}")
                        if hasattr(result.channel, 'alternatives') and result.channel.alternatives:
                            alt = result.channel.alternatives[0]
                            print(f"Alternative has words: {hasattr(alt, 'words')}")
                            if hasattr(alt, 'words') and alt.words:
                                print(f"First few words: {[{w.word if hasattr(w, 'word') else str(w): getattr(w, 'speaker', 'no_speaker')} for w in alt.words[:3]]}")
                    
                    # Try multiple ways to extract speaker information
                    try:
                        # Method 1: Check if words have speaker information
                        if (hasattr(result.channel.alternatives[0], 'words') and 
                            result.channel.alternatives[0].words and 
                            len(result.channel.alternatives[0].words) > 0):
                            
                            # Look for speaker in the first word
                            first_word = result.channel.alternatives[0].words[0]
                            if hasattr(first_word, 'speaker') and first_word.speaker is not None:
                                speaker_id = first_word.speaker
                                print(f"Found speaker from first word: {speaker_id}")
                            
                            # If not found, check all words for speaker info
                            if speaker_id is None:
                                for word in result.channel.alternatives[0].words:
                                    if hasattr(word, 'speaker') and word.speaker is not None:
                                        speaker_id = word.speaker
                                        print(f"Found speaker from word '{word.word if hasattr(word, 'word') else str(word)}': {speaker_id}")
                                        break
                        
                        # Method 2: Check if there's speaker info at the alternative level
                        if speaker_id is None and hasattr(result.channel.alternatives[0], 'speaker'):
                            speaker_id = result.channel.alternatives[0].speaker
                            print(f"Found speaker at alternative level: {speaker_id}")
                        
                        # Method 3: Check if there's speaker info at the channel level
                        if speaker_id is None and hasattr(result.channel, 'speaker'):
                            speaker_id = result.channel.speaker
                            print(f"Found speaker at channel level: {speaker_id}")
                            
                    except Exception as e:
                        print(f"Error extracting speaker info: {e}")
                    
                    # Fallback: Improved speaker inference if no speaker data from Deepgram
                    if speaker_id is None:
                        import time
                        current_time = time.time()
                        
                        # Initialize session tracking if needed
                        if not hasattr(self, '_session_current_speaker'):
                            self._session_current_speaker = {}
                        if not hasattr(self, '_session_speaker_patterns'):
                            self._session_speaker_patterns = {}
                        
                        if session_id not in self._session_current_speaker:
                            self._session_current_speaker[session_id] = 1
                        if session_id not in self._session_speaker_patterns:
                            self._session_speaker_patterns[session_id] = {
                                'last_speaker': 1,
                                'utterance_count': 0,
                                'speaker_1_words': 0,
                                'speaker_2_words': 0
                            }
                        
                        patterns = self._session_speaker_patterns[session_id]
                        
                        # Improved heuristics for speaker detection
                        last_time_key = f'_last_transcript_time_{session_id}'
                        time_gap = 0
                        if hasattr(self, last_time_key):
                            time_gap = current_time - getattr(self, last_time_key)
                        
                        # Analyze sentence patterns for speaker inference
                        sentence_lower = sentence.lower()
                        word_count = len(sentence.split())
                        
                        # Medical conversation patterns
                        doctor_phrases = ["let's", "i'm going to", "can you", "how are", "what brings", 
                                        "i need to", "we should", "i'd like to", "tell me about"]
                        patient_phrases = ["i have", "it hurts", "i feel", "my", "i can't", 
                                         "i've been", "i think", "i'm worried", "i'm having"]
                        
                        is_likely_doctor = any(phrase in sentence_lower for phrase in doctor_phrases)
                        is_likely_patient = any(phrase in sentence_lower for phrase in patient_phrases)
                        
                        # Decision logic for speaker identification
                        should_switch_speaker = False
                        
                        # Rule 1: Long pause (>2 seconds) suggests speaker change
                        if time_gap > 2.0:
                            should_switch_speaker = True
                            print(f"Speaker change due to {time_gap:.1f}s pause")
                        
                        # Rule 2: Short utterance after long one suggests response/question
                        elif word_count < 5 and patterns['utterance_count'] > 0:
                            should_switch_speaker = True
                            print(f"Speaker change due to short response ({word_count} words)")
                        
                        # Rule 3: Medical conversation patterns
                        elif is_likely_doctor and patterns['last_speaker'] == 2:
                            should_switch_speaker = True
                            print("Speaker change: detected doctor language pattern")
                        elif is_likely_patient and patterns['last_speaker'] == 1:
                            should_switch_speaker = True
                            print("Speaker change: detected patient language pattern")
                        
                        # Rule 4: Balance conversation - prevent one speaker dominating
                        elif patterns['speaker_1_words'] > patterns['speaker_2_words'] + 50 and patterns['last_speaker'] == 1:
                            should_switch_speaker = True
                            print("Speaker change: balancing conversation")
                        elif patterns['speaker_2_words'] > patterns['speaker_1_words'] + 50 and patterns['last_speaker'] == 2:
                            should_switch_speaker = True
                            print("Speaker change: balancing conversation")
                        
                        # Apply speaker change
                        if should_switch_speaker:
                            current_speaker = 2 if patterns['last_speaker'] == 1 else 1
                            self._session_current_speaker[session_id] = current_speaker
                            patterns['last_speaker'] = current_speaker
                            print(f"Switched to Speaker {current_speaker}")
                        else:
                            current_speaker = patterns['last_speaker']
                        
                        # Update patterns
                        patterns['utterance_count'] += 1
                        if current_speaker == 1:
                            patterns['speaker_1_words'] += word_count
                        else:
                            patterns['speaker_2_words'] += word_count
                        
                        setattr(self, last_time_key, current_time)
                        speaker_id = current_speaker - 1  # Convert to 0-based for consistency
                        print(f"Final speaker assignment: Speaker {current_speaker} (words: {word_count}, gap: {time_gap:.1f}s)")
                    
                    # Format the transcript with speaker information
                    if speaker_id is not None:
                        formatted_sentence = f"Speaker {speaker_id + 1}: {sentence}"
                        print(f"Streaming transcript: Speaker {speaker_id + 1}: '{sentence[:50]}...'")
                    else:
                        formatted_sentence = sentence
                        print(f"Streaming transcript (no speaker): '{sentence[:50]}...'")
                    
                    self.connection_transcripts[session_id] += " " + formatted_sentence
                    
                    # Call the callback with speaker-labeled transcript
                    transcript_data = {
                        'text': sentence,
                        'speaker': speaker_id + 1 if speaker_id is not None else None,
                        'formatted_text': formatted_sentence,
                        'full_transcript': self.connection_transcripts[session_id]
                    }
                    on_transcript_callback(transcript_data)
            
            def on_metadata(connection_self, metadata, **kwargs):
                print(f"Streaming metadata: {metadata}")
            
            def on_close(connection_self, **kwargs):
                print(f"Streaming connection closed for session: {session_id}")
            
            def on_error(connection_self, error, **kwargs):
                print(f"Streaming error for session {session_id}: {error}")
            
            # Register event handlers
            print("Registering event handlers...")
            connection.on(LiveTranscriptionEvents.Open, on_open)
            connection.on(LiveTranscriptionEvents.Transcript, on_message)
            connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
            connection.on(LiveTranscriptionEvents.Close, on_close)
            connection.on(LiveTranscriptionEvents.Error, on_error)
            print("Event handlers registered successfully")
            
            # Start the connection
            print("Starting Deepgram connection...")
            connection.start(self.streaming_options)
            print("Deepgram connection started successfully")
            
            return True
                
        except Exception as e:
            print(f"Error starting streaming session: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def send_audio_chunk_to_stream(self, session_id: str, audio_bytes: bytes) -> bool:
        """Send audio chunk to streaming connection"""
        try:
            connection = self.connections.get(session_id)
            if connection:
                connection.send(audio_bytes)
                return True
            else:
                print(f"No streaming connection found for session: {session_id}")
                return False
        except Exception as e:
            print(f"Error sending audio chunk to stream: {e}")
            return False
    
    def stop_streaming_session(self, session_id: str) -> str:
        """Stop streaming session and return final transcript"""
        try:
            connection = self.connections.get(session_id)
            if connection:
                connection.finish()
                del self.connections[session_id]
            
            # Get final transcript
            final_transcript = self.connection_transcripts.get(session_id, "")
            if session_id in self.connection_transcripts:
                del self.connection_transcripts[session_id]
            
            print(f"Streaming session stopped for: {session_id}")
            return final_transcript
            
        except Exception as e:
            print(f"Error stopping streaming session: {e}")
            return ""
    
    def correct_speaker(self, session_id: str, speaker_number: int) -> bool:
        """Manually correct the current speaker for a session"""
        try:
            if not hasattr(self, '_session_current_speaker'):
                self._session_current_speaker = {}
            if not hasattr(self, '_session_speaker_patterns'):
                self._session_speaker_patterns = {}
                
            self._session_current_speaker[session_id] = speaker_number
            
            # Update patterns if they exist
            if session_id in self._session_speaker_patterns:
                self._session_speaker_patterns[session_id]['last_speaker'] = speaker_number
                
            print(f"Speaker manually corrected to Speaker {speaker_number} for session {session_id}")
            return True
        except Exception as e:
            print(f"Error correcting speaker: {e}")
            return False
    
    def get_session_speaker_stats(self, session_id: str) -> dict:
        """Get speaker statistics for a session"""
        try:
            if (hasattr(self, '_session_speaker_patterns') and 
                session_id in self._session_speaker_patterns):
                patterns = self._session_speaker_patterns[session_id]
                return {
                    'current_speaker': patterns['last_speaker'],
                    'speaker_1_words': patterns['speaker_1_words'],
                    'speaker_2_words': patterns['speaker_2_words'],
                    'total_utterances': patterns['utterance_count']
                }
            return {'current_speaker': 1, 'speaker_1_words': 0, 'speaker_2_words': 0, 'total_utterances': 0}
        except Exception as e:
            print(f"Error getting speaker stats: {e}")
            return {'current_speaker': 1, 'speaker_1_words': 0, 'speaker_2_words': 0, 'total_utterances': 0} 