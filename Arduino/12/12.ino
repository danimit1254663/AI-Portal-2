#define _LCD_TYPE 1

#include "LCD_1602_RUS_ALL.h"

LCD_1602_RUS lcd(0x27, 16, 2);

String line1 = "";
String line2 = "";
String inputBuffer = "";

int currentLine = 0;


void setup() {

  Serial.begin(9600);

  delay(500);

  lcd.init();
  lcd.backlight();
  lcd.clear();

  lcd.setCursor(0, 0);
  lcd.print("JARVIS READY");

  lcd.setCursor(0, 1);
  lcd.print("Send text...");

  Serial.println("JARVIS READY");
  Serial.println("Waiting...");
}


void loop() {

  while (Serial.available() > 0) {

    char c = Serial.read();


    // --------------------------------------------------------
    // CR игнорируем
    // --------------------------------------------------------

    if (c == '\r') {
      continue;
    }


    // --------------------------------------------------------
    // Получили конец строки
    // --------------------------------------------------------

    if (c == '\n') {


      // ------------------------------------------------------
      // Первая строка
      // ------------------------------------------------------

      if (currentLine == 0) {

        line1 = inputBuffer;

        inputBuffer = "";

        currentLine = 1;

        continue;
      }


      // ------------------------------------------------------
      // Вторая строка
      // ------------------------------------------------------

      if (currentLine == 1) {

        line2 = inputBuffer;

        inputBuffer = "";

        currentLine = 0;


        // ----------------------------------------------------
        // НИКАКИХ substring()
        // НИКАКИХ length() > 16
        //
        // Потому что русский UTF-8 занимает несколько байт.
        // ----------------------------------------------------


        Serial.print("LINE1: ");
        Serial.println(line1);

        Serial.print("LINE2: ");
        Serial.println(line2);


        // ----------------------------------------------------
        // LCD
        // ----------------------------------------------------

        lcd.clear();

        lcd.printPage(
          line1.c_str(),
          line2.c_str()
        );


        // ----------------------------------------------------
        // Очистка
        // ----------------------------------------------------

        line1 = "";
        line2 = "";
      }


      continue;
    }


    // --------------------------------------------------------
    // Принимаем UTF-8 байты
    // --------------------------------------------------------

    if (inputBuffer.length() < 200) {

      inputBuffer += c;
    }
  }
}
