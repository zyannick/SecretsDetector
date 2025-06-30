#include <immintrin.h>
#include <cstdint>
#include <cmath>
#include <algorithm>
#include <string>

extern "C" {
    
    void calculate_char_freq_avx2_optimized(const char* input_str, const int length, int* freq_array) {
        for (int i = 0; i < 256; ++i) {
            freq_array[i] = 0;
        }
        
        const int simd_end = length - (length % 32);
        for (int i = 0; i < simd_end; i += 32) {
            const __m256i chunk = _mm256_loadu_si256((const __m256i*)(input_str + i));
            
            alignas(32) uint8_t bytes[32];
            _mm256_storeu_si256((__m256i*)bytes, chunk);
            
            freq_array[bytes[0]]++; freq_array[bytes[1]]++; freq_array[bytes[2]]++; freq_array[bytes[3]]++;
            freq_array[bytes[4]]++; freq_array[bytes[5]]++; freq_array[bytes[6]]++; freq_array[bytes[7]]++;
            freq_array[bytes[8]]++; freq_array[bytes[9]]++; freq_array[bytes[10]]++; freq_array[bytes[11]]++;
            freq_array[bytes[12]]++; freq_array[bytes[13]]++; freq_array[bytes[14]]++; freq_array[bytes[15]]++;
            freq_array[bytes[16]]++; freq_array[bytes[17]]++; freq_array[bytes[18]]++; freq_array[bytes[19]]++;
            freq_array[bytes[20]]++; freq_array[bytes[21]]++; freq_array[bytes[22]]++; freq_array[bytes[23]]++;
            freq_array[bytes[24]]++; freq_array[bytes[25]]++; freq_array[bytes[26]]++; freq_array[bytes[27]]++;
            freq_array[bytes[28]]++; freq_array[bytes[29]]++; freq_array[bytes[30]]++; freq_array[bytes[31]]++;
        }
        
        for (int i = simd_end; i < length; ++i) {
            freq_array[static_cast<unsigned char>(input_str[i])]++;
        }
    }
    
    double calculate_entropy_for_secrets(const char* input_str, const int length) {
        if (length == 0) return 0.0;
        
        int freq_array[256];
        calculate_char_freq_avx2_optimized(input_str, length, freq_array);
        
        double entropy = 0.0;
        const double len_d = static_cast<double>(length);
        

        for (int i = 0; i < 256; ++i) {
            if (freq_array[i] > 0) {
                double prob = static_cast<double>(freq_array[i]) / len_d;
                entropy -= prob * log2(prob);
            }
        }
        
        return entropy;
    }
    
    struct EntropyAnalysis {
        double overall_entropy;
        double max_substring_entropy;
        int high_entropy_regions;
        bool likely_secret;
    };
    
    EntropyAnalysis analyze_string_for_secrets(const char* input_str, const int length) {
        EntropyAnalysis result = {0};
        
        if (length < 8) {
            result.likely_secret = false;
            return result;
        }
        
        result.overall_entropy = calculate_entropy_for_secrets(input_str, length);
        
        const int window_size = 32;  
        const double entropy_threshold = 4.5;  
        
        double max_entropy = 0.0;
        int high_entropy_count = 0;
        
        for (int i = 0; i <= length - window_size; i += 8) {  
            double window_entropy = calculate_entropy_for_secrets(input_str + i, window_size);
            
            if (window_entropy > entropy_threshold) {
                high_entropy_count++;
            }
            
            if (window_entropy > max_entropy) {
                max_entropy = window_entropy;
            }
        }
        
        result.max_substring_entropy = max_entropy;
        result.high_entropy_regions = high_entropy_count;
        
        result.likely_secret = (result.overall_entropy > 4.0) || 
                              (high_entropy_count > 0 && result.max_substring_entropy > 5.0);
        
        return result;
    }
    
    bool detect_api_key_pattern_avx2(const char* input_str, const int length) {
        if (length < 20) return false;
        
        const __m256i base64_chars_lower = _mm256_setr_epi8(
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
            'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '+', '/', '0', '1', '2', '3'
        );
        
        int consecutive_base64 = 0;
        int max_consecutive = 0;
        
        for (int i = 0; i < length - 31; i += 32) {
            const __m256i chunk = _mm256_loadu_si256((const __m256i*)(input_str + i));
            
            __m256i is_digit = _mm256_and_si256(
                _mm256_cmpgt_epi8(chunk, _mm256_set1_epi8('0' - 1)),
                _mm256_cmpgt_epi8(_mm256_set1_epi8('9' + 1), chunk)
            );
            
            __m256i is_upper = _mm256_and_si256(
                _mm256_cmpgt_epi8(chunk, _mm256_set1_epi8('A' - 1)),
                _mm256_cmpgt_epi8(_mm256_set1_epi8('Z' + 1), chunk)
            );
            
            __m256i is_lower = _mm256_and_si256(
                _mm256_cmpgt_epi8(chunk, _mm256_set1_epi8('a' - 1)),
                _mm256_cmpgt_epi8(_mm256_set1_epi8('z' + 1), chunk)
            );
            
            __m256i is_plus = _mm256_cmpeq_epi8(chunk, _mm256_set1_epi8('+'));
            __m256i is_slash = _mm256_cmpeq_epi8(chunk, _mm256_set1_epi8('/'));
            
            __m256i is_base64 = _mm256_or_si256(
                _mm256_or_si256(_mm256_or_si256(is_digit, is_upper), is_lower),
                _mm256_or_si256(is_plus, is_slash)
            );
            
            uint32_t mask = _mm256_movemask_epi8(is_base64);
            
            if (mask == 0xFFFFFFFF) {  
                consecutive_base64 += 32;
            } else {
                max_consecutive = std::max(max_consecutive, consecutive_base64);
                consecutive_base64 = 0;
            }
        }
        
        max_consecutive = std::max(max_consecutive, consecutive_base64);
        
        return max_consecutive >= 20;
    }
}

class SecretsDetector {
public:
    static bool isLikelySecret(const std::string& text) {
        EntropyAnalysis analysis = analyze_string_for_secrets(text.c_str(), text.length());
        return analysis.likely_secret || detect_api_key_pattern_avx2(text.c_str(), text.length());
    }
    
    static double getEntropy(const std::string& text) {
        return calculate_entropy_for_secrets(text.c_str(), text.length());
    }
    
    static EntropyAnalysis analyzeForSecrets(const std::string& text) {
        return analyze_string_for_secrets(text.c_str(), text.length());
    }
};