# Kryptowaluta - projekt

## Instrukcja użytkownika

### 1. Uruchomienie

Pojedynczego Node'a można uruchomić wpisując w terminalu polecenie:

```
python server.py
``` 

lub otwierając plik `server.bat`.

Powinna wówczas wyświetlić się konsola, w której należy podać numer portu dla danego Node'a (z przedziału 5000 - 6000).
Numer portu jest jednocześnie identyfikatorem danego Node'a (wszystkie Node'y mają ten sam adres IP - "127.0.0.1", a
różnią się numerami portu). Po prawidłowym zdefiniowaniu portu, Node generuje swoje klucze prywatny i publiczny,
zaszyfrowuje i zapisuje do pliku swój klucz prywatny, inicjuje pustą listę węzłów i wpisuje do niej własny klucz
publiczny i adres IP wraz z portem.

### 2. Połączenie

Gdy przynajmniej dwa Node'y sa uruchomione, mogą one połączyć się ze sobą. W tym celu w terminalu wybranego Node'a
należy wpisać komendę `connect` a następnie podać numer portu drugiego Node'a. Wówczas pierwszy węzeł wyśle do drugiego
swój klucz publiczny i adres IP, drugi węzeł w odpowiedzi odeśle swoją listę węzłów, dopisze do niej nowego Node'a i
powiadomi o tym pozostałe węzły (roześle klucz publiczny i adres IP nowego Node'a).

### 3. Wysłanie wiadomości

Gdy co najmniej dwa Node'y są ze sobą połączone (mają swoje klucze publiczne i adresy), mogę wymienić między sobą
wiadomość z podpisem, świadczącym o wiarygodności nadawcy. Aby wysłać wiadomość, należy w terminalu wybranego Node'a
wpisać komendę `send`, a następnie podać numer portu węzła, do którego chcemy ją wysłać i wpisać tekst wiadomości.
Wówczas wybrany Node podpisze wiadomość korzystając z własnego klucza prywatnego i wyśle ją do drugiego węzła. Gdy węzeł
ten odbierze wiadomość, wyszuka w swojej liście węzłów klucz publiczny Node'a, od którego wiadomość przyszła i użyje go
do weryfikacji podpisu. Jeśli wynik będzie pozytywny, a więc nadawca zostanie uwiarygodniony, wiadomość zostanie
wyświetlona w konsoli a nadawca zostanie powiadomiony o potwierdzeniu wiarygodności, w przeciwnym razie wiadomość nie
zostanie wyświetlona. Pojawi się jedynie komunikat o niepotwierdzeniu nadesłanej wiadomości, a jej nadawca zostanie
poinformowany o niepowodzeniu weryfikacji.

Aby celowo wysłać wiadomość z niepoprawnym podpisem, należy w konsoli wybranego węzła wpisać komendę `cheat`, a
następnie podać numer portu adresata i tekst wiadomości.

### 4. Wysyłanie transakcji

Node zacznie wysyłanie transakcji zawierających numer identyfikacyjny (UUID) oraz podpis (Signature) po wpisaniu 
w terminalu komendy: `transaction`. Wiadomości są wysyłane do wszystkich połączonych node'ów (do wszystkich adresów IP 
zapisanych w liście node'ów).

### 5. Kopanie

Aby rozpocząć proces kopania, należy w terminalu dowolnego node'a wpisać polecenie: `mining`. Wówczas node ten 
poinformuje o rozpoczęciu kopania pozostałe węzły. Roześle on ustalony czas, w jakim należy rozpocząć kopanie. 
Wszystkie nody będą oczekiwać na rozpoczęcie kopania, sprawdzając nieustannie aktualny czas i porównując 
z ustalonym czasem startu. Gdy kopanie się rozpocznie, node'y zaczynają sprawdzać kolejne warrtości nonce w poszukiwaniu
odpowiedniego hasha. Kolejne wyniki hash'y są drukowane w konsoli. Gdy któryś z node'ów znajdzie spełniający warunki 
hash - poinformuje pozostałych o zakończeniu kopania. Pozostałe node'y przestają wówczas kopać. I oczekują na przysłanie
od zwycięskiego węzła nowego bloku. Sprawdzają następnie jego poprawność i dołączają do blockchainu. 

### 6. Wyświetlanie
Aby wyświetlić aktualną listę transakcji należy w teminalu węzła wpisać komendę `print transactions`. 
Aby wyświetlić cały blockchain należy wpisać polecenie `print blockchain`.

### 7. Koniec pracy

Aby zakończyć działanie wybranego węzła, należy w jego terminalu wpisać komendę `stop`, która zakończy wątek konsoli, a
następnie przycisnąć jednocześnie `CTRL+C`, aby zakończyć pracę serwera.

<br>

**Autorzy:**

Anna Stpiczyńska

Kacper Kiciński
