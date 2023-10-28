document.addEventListener('DOMContentLoaded', function() {
    // Load stocks
    if (watchlist) {
        load_watched_stocks()
    } else {
        load_stocks();
    }
})


function load_stocks() {

    // Clear and show the stocks view
    document.querySelector('#stocks').innerHTML = '';
    document.querySelector('#stocks').style.display = 'block';

    // Load stocks
    fetch(`/stocks`)
    .then(response => response.json())
    .then(stocks => {

        // If user is logged on, include column with watched stocks
        if (userId) {
            // Load watched stocks
            fetch(`/watched_stocks/${userId}`)
            .then(response => response.json())
            .then(watched_stocks => {

                // Add watched key to stocks, by checking if a stock is also in the watched stocks
                stocks = stocks.map(s => ({...s, watched: watched_stocks.some(ws => ws.id === s.id)}));

                // Create Tabulator on DOM element
                const table = new Tabulator("#stocks", {
                    height: "100%",
                    data: stocks,
                    layout: "fitData",
                    columns: [
                        {title: "Name", field: "name", width: 150},
                        {title: "Symbol", field: "symbol", width: 100},
                        {title: "Exchange", field: "exchange", width: 100},
                        {title: "ISIN", field: "ISIN", width: 150},
                        {title: "Watchlist", field: "watched", formatter: "tickCross", width: 100},
                    ],
                });
            });
        } else {
            // Create Tabulator on DOM element
            const table = new Tabulator("#stocks", {
                height: "100%",
                data: stocks,
                layout: "fitData",
                columns: [
                    {title: "Name", field: "name", width: 150},
                    {title: "Symbol", field: "symbol", width: 150},
                    {title: "Exchange", field: "exchange", width: 150},
                    {title: "ISIN", field: "ISIN", width: 150},
                ],
            });
        }
    });
}


function load_watched_stocks() {

    // Clear and show the stocks view
    document.querySelector('#stocks').innerHTML = '';
    document.querySelector('#stocks').style.display = 'block';

    // Load stocks
    fetch(`/watched_stocks/${userId}`)
    .then(response => response.json())
    .then(watched_stocks => {

        // Add watched key to stocks
        watched_stocks = watched_stocks.map(s => ({...s, watched: true}));

        // Create Tabulator on DOM element
        const table = new Tabulator("#stocks", {
            height: "100%",
            data: watched_stocks,
            layout: "fitData",
            columns: [
                {title: "Name", field: "name", width: 150},
                {title: "Symbol", field: "symbol", width: 150},
                {title: "Exchange", field: "exchange", width: 150},
                {title: "ISIN", field: "ISIN", width: 150},
                {title: "Watchlist", field: "watched", formatter: "tickCross", width: 150},
            ],
        });
    });
}
