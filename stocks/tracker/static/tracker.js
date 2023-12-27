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
                    columns: [
                        {title: "Name", field: "name", width: 150},
                        {title: "Symbol", field: "symbol", width: 100},
                        {title: "Exchange", field: "exchange", width: 100},
                        {title: "ISIN", field: "ISIN", width: 150},
                        {title: "Price", field: "price", width: 150, formatter: currencyFormatter},
                        {title: "Watch", field: "watched", formatter: "tickCross", hozAlign: "center",
                            cellClick: function (e, cell) { toggleStockWatch(cell) }, width: 80},
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
                {title: "Watch", field: "watched", formatter: "tickCross", hozAlign: "center",
                    cellClick: function (e, cell) { toggleStockWatch(cell) }, width: 80},
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
    .then(portfolio => {

        // Create Tabulator on DOM element
        const table = new Tabulator("#portfolio", {
            height: "100%",
            data: portfolio['stocks'],
            layout: "fitData",
            columns: [
                {title: "Name", field: "name", width: 150},
                {title: "Symbol", field: "symbol", width: 100},
                {title: "Exchange", field: "exchange", width: 100},
                {title: "ISIN", field: "ISIN", width: 150},
                {title: "Amount", field: "amount", width: 100},
                {title: "Price", field: "price", width: 100, formatter: currencyFormatter},
                {title: "Real. price", field: "realized_price", width: 120, formatter: currencyFormatter},
                {title: "Costs", field: "total_cost", width: 100, formatter: currencyFormatter,
                    bottomCalc: () => { return portfolio['metrics']['total_cost'] },
                    bottomCalcFormatter: pnlFormatter,
                    bottomCalcFormatterParams: { currency: portfolio['metrics']['currency'] }},
                {title: "Unr. PnL", field: "unrealized_pnl", width: 120, formatter: pnlFormatter,
                    bottomCalc: () => { return portfolio['metrics']['unrealized_pnl'] },
                    bottomCalcFormatter: pnlFormatter,
                    bottomCalcFormatterParams: { currency: portfolio['metrics']['currency'] }},
                {title: "Unr. PnL %", field: "unrealized_pnl_percentage", width: 120, formatter: percentageFormatter},
                // {title: "Rea. PnL", field: "realized_pnl", width: 100, formatter: pnlFormatter,
            ],
        });
    });
}


function toggleStockWatch(cell) {

    // Get stock ID
    const stockId = cell.getRow().getData().id;

    // Get watched status
    const watched = cell.getRow().getData().watched;

    // Toggle watched status
    fetch(`/toggle_watch/${stockId}`, {
        method: 'PUT',
    })
    .then(result => {
        // Update watched status in row
        // TODO: Optionally update table when watch is removed from watchlist (required in assignment to update by JS?)
        if (result.status === 200 || result.status === 201) {
            cell.getRow().update({watched: !watched});
        }
    });
}