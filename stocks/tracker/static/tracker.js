document.addEventListener('DOMContentLoaded', function() {
    // Load stocks
    if (watchlist) {
        load_watched_stocks();
    } else if (portfolios) {
        load_portfolio();
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
            fetch(`/watched_stocks`)
            .then(response => response.json())
            .then(watched_stocks => {

                // Add watched key to stocks, by checking if a stock is also in the watched stocks
                stocks = stocks.map(s => ({...s, watched: watched_stocks.some(ws => ws.id === s.id)}));

                // Create Tabulator on DOM element
                const table = new Tabulator("#stocks", {
                    height: "100%",
                    data: stocks,
                    layout: "fitData",
                    // TODO: Include currency in hidden column, once added to Stock model (instead of transaction)
                    columns: [
                        {title: "Name", field: "name", width: 150},
                        {title: "Symbol", field: "symbol", width: 100},
                        {title: "Exchange", field: "exchange", width: 100},
                        {title: "ISIN", field: "ISIN", width: 150},
                        {title: "Price", field: "price", width: 150, formatter: currencyFormatter},
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
                // TODO: Include currency in hidden column, once added to Stock model (instead of transaction)
                columns: [
                    {title: "Name", field: "name", width: 150},
                    {title: "Symbol", field: "symbol", width: 150},
                    {title: "Exchange", field: "exchange", width: 150},
                    {title: "ISIN", field: "ISIN", width: 150},
                    {title: "Price", field: "price", width: 150, formatter: currencyFormatter},
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
    fetch(`/watched_stocks`)
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
                {title: "Price", field: "price", width: 150, formatter: currencyFormatter},
                {title: "Watchlist", field: "watched", formatter: "tickCross", width: 150},
            ],
        });
    });
}


function load_portfolio() {

    // Clear and show the stocks view
    document.querySelector('#portfolio').innerHTML = '';
    document.querySelector('#portfolio').style.display = 'block';

    // Load portfolio
    fetch(`/portfolio/${portfolioId}`)
    .then(response => response.json())
    .then(portfolio_stocks => {

        // Create Tabulator on DOM element
        const table = new Tabulator("#portfolio", {
            height: "100%",
            data: portfolio_stocks,
            layout: "fitData",
            columns: [
                {title: "Name", field: "name", width: 150},
                {title: "Symbol", field: "symbol", width: 150},
                {title: "Exchange", field: "exchange", width: 150},
                {title: "ISIN", field: "ISIN", width: 150},
                {title: "Currency", field: "currency", visible: false},
                {title: "Amount", field: "amount", width: 150},
                {title: "Price", field: "price", width: 150, formatter: currencyFormatter},
                {title: "Realized price", field: "realized_price", width: 150, formatter: currencyFormatter},
                // TODO: Implement summation with currency conversion (exchangerates API?), including addition of classes
                {title: "Unrealized PnL", field: "unrealized_pnl", width: 150, formatter: pnlFormatter, bottomCalc: "sum"},
            ],
        });
    });
}


// TODO: Move to a (tabulator) utils file
function currencyFormatter(cell, formatterParams, onRendered) {
    // Add class based on currency
    if (cell.getData().currency) { cell.getElement().classList.add(cell.getData().currency.toLowerCase()); }

    // Return value rounded to two decimals
    return parseFloat(cell.getValue()).toFixed(2);
}

function pnlFormatter(cell, formatterParams, onRendered) {

    // Get value from cell
    const value = cell.getValue();

    // Add 'profit' or 'loss' class depending on value
    if (value > 0) {
        cell.getElement().classList.add('profit');
    } else if (value < 0) {
        cell.getElement().classList.add('loss');
    }

    return currencyFormatter(cell, formatterParams, onRendered);
}
