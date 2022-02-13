# Victron_BatteryFullthenSoC100
Script which set the DBus SoC too 100% if there is enough export but the Battery isnt loading anymore.<br>
Dieses Script überprüft wieviel Energie exportiert wird und ob der Akku dementsprechend geladen wird.<br>
Wenn der Akku nicht geladen wird, muss er voll sein -> 100% SoC wid gesetzt.<br>
Script funktioniert nur in On-Grid Systemen, da sonst nicht exportiert wird.<br>
