#ifndef LOG_H
#define LOG_H

#include <Arduino.h>

class Log {
private:
    static void stampaTimestamp() {
        unsigned long millisec = millis();
        unsigned long secondi = millisec / 1000;
        unsigned long minuti = secondi / 60;
        unsigned long ore = minuti / 60;
        
        Serial.printf("[%02lu:%02lu:%02lu.%03lu] ", 
            ore % 24, minuti % 60, secondi % 60, millisec % 1000);
    }

public:
    template<typename... Args>
    static void stampaNormale(const char* format, Args... args) {
        stampaTimestamp();
        Serial.printf(format, args...);
        Serial.println();
    }

    template<typename... Args>
    static void stampaAllarme(const char* format, Args... args) {
        stampaTimestamp();
        Serial.print("\033[31m");
        Serial.printf(format, args...);
        Serial.println("\033[0m");
    }

    template<typename... Args>
    static void stampaWarning(const char* format, Args... args) {
        stampaTimestamp();
        Serial.print("\033[33m");
        Serial.printf(format, args...);
        Serial.println("\033[0m");
    }

    template<typename... Args>
    static void stampaInfo(const char* format, Args... args) {
        stampaTimestamp();
        Serial.print("\033[34m");
        Serial.printf(format, args...);
        Serial.println("\033[0m");
    }
};

#endif