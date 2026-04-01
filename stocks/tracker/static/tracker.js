document.addEventListener('DOMContentLoaded', function () {
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
                        stocks = stocks.map(s => ({ ...s, watched: watched_stocks.some(ws => ws.id === s.id) }));

                        // Create Tabulator on DOM element
                        const table = new Tabulator("#stocks", {
                            height: "100%",
                            data: stocks,
                            layout: "fitData",
                            columns: [
                                { title: "Name", field: "name", width: 150 },
                                { title: "Symbol", field: "symbol", width: 100 },
                                { title: "Exchange", field: "exchange", width: 100 },
                                { title: "ISIN", field: "ISIN", width: 150 },
                                { title: "Price", field: "price", width: 80, formatter: currencyFormatter },
                                {
                                    title: "Watch", field: "watched", formatter: "tickCross", hozAlign: "center",
                                    cellClick: function (e, cell) { toggleStockWatch(cell) }, width: 80
                                },
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
                        { title: "Name", field: "name", width: 150 },
                        { title: "Symbol", field: "symbol", width: 150 },
                        { title: "Exchange", field: "exchange", width: 150 },
                        { title: "ISIN", field: "ISIN", width: 150 },
                        { title: "Price", field: "price", width: 80, formatter: currencyFormatter },
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
            watched_stocks = watched_stocks.map(s => ({ ...s, watched: true }));

            // Create Tabulator on DOM element
            const table = new Tabulator("#stocks", {
                height: "100%",
                data: watched_stocks,
                layout: "fitData",
                columns: [
                    { title: "Name", field: "name", width: 150 },
                    { title: "Symbol", field: "symbol", width: 150 },
                    { title: "Exchange", field: "exchange", width: 150 },
                    { title: "ISIN", field: "ISIN", width: 150 },
                    { title: "Price", field: "price", width: 80, formatter: currencyFormatter },
                    {
                        title: "Watch", field: "watched", formatter: "tickCross", hozAlign: "center",
                        cellClick: function (e, cell) { toggleStockWatch(cell) }, width: 80
                    },
                ],
            });
        });
}


function load_portfolio() {

    // Load portfolio if portfolioId is specified
    if (portfolioId) {
        fetch(`/portfolio/${portfolioId}`)
            .then(response => response.json())
            .then(portfolio => {

                // Create Tabulator on DOM element with portfolio stocks, if stocks div can be found
                if (document.querySelector('#stocks')) {
                    new Tabulator("#stocks", {
                        maxHeight: "100%",
                        data: portfolio['stocks'],
                        layout: "fitDataTable",
                        columns: [
                            { title: "Name", field: "name", width: 150, headerHozAlign: "center", frozen: true },
                            {
                                title: "General information", headerHozAlign: "center", columns: [
                                    { title: "Symbol", field: "symbol", width: 75, headerVertical: true },
                                    { title: "Exchange", field: "exchange", width: 75, headerVertical: true },
                                    { title: "ISIN", field: "ISIN", width: 150, headerVertical: true },
                                    { title: "Amount", field: "amount", width: 75, headerVertical: true },
                                    { title: "Price", field: "price", width: 75, headerVertical: true, formatter: currencyFormatter },
                                    { title: "Weight", field: "weight", width: 75, headerVertical: true, formatter: percentageFormatter },
                                ]
                            },
                            {
                                title: "Performance metrics", headerHozAlign: "center", columns: [
                                    { title: "Cost basis", field: "cost_basis", width: 75, headerVertical: true, formatter: currencyFormatter },
                                    {
                                        title: "Costs", field: "total_cost", width: 75, headerVertical: true, formatter: currencyFormatter,
                                        bottomCalc: () => { return portfolio['metrics']['total_cost'] },
                                        bottomCalcFormatter: currencyFormatter,
                                        bottomCalcFormatterParams: { currency: portfolio['portfolio']['currency'] }
                                    },
                                    {
                                        title: "Unr. PnL", field: "unrealized_pnl", width: 75, headerVertical: true, formatter: pnlFormatter,
                                        bottomCalc: () => { return portfolio['metrics']['unrealized_pnl'] },
                                        bottomCalcFormatter: pnlFormatter,
                                        bottomCalcFormatterParams: { currency: portfolio['portfolio']['currency'] }
                                    },
                                    {
                                        title: "Unr. PnL %", field: "unrealized_pnl_percentage", width: 75, headerVertical: true, formatter: percentageFormatter,
                                        bottomCalc: () => { return portfolio['metrics']['unrealized_pnl_percentage'] },
                                        bottomCalcFormatter: percentageFormatter
                                    },
                                    {
                                        title: "Real. PnL", field: "realized_pnl", width: 75, headerVertical: true, formatter: pnlFormatter,
                                        bottomCalc: () => { return portfolio['metrics']['realized_pnl'] },
                                        bottomCalcFormatter: pnlFormatter,
                                        bottomCalcFormatterParams: { currency: portfolio['portfolio']['currency'] }
                                    },
                                    {
                                        title: "Real. PnL %", field: "realized_pnl_percentage", width: 75, headerVertical: true, formatter: percentageFormatter,
                                        bottomCalc: () => { return portfolio['metrics']['realized_pnl_percentage'] },
                                        bottomCalcFormatter: percentageFormatter
                                    },
                                    {
                                        title: "Fiat div.", field: "total_dividend", width: 75, headerVertical: true, formatter: currencyFormatter,
                                        bottomCalc: () => { return portfolio['metrics']['total_dividend'] },
                                        bottomCalcFormatter: currencyFormatter,
                                        bottomCalcFormatterParams: { currency: portfolio['portfolio']['currency'] }
                                    },
                                    {
                                        title: "Tot. ret.", field: "total_return", width: 75, headerVertical: true, formatter: pnlFormatter,
                                        bottomCalc: () => { return portfolio['metrics']['total_return'] },
                                        bottomCalcFormatter: pnlFormatter,
                                        bottomCalcFormatterParams: { currency: portfolio['portfolio']['currency'] }
                                    },
                                    {
                                        title: "Tot. ret. %", field: "total_return_percentage", width: 75, headerVertical: true, formatter: percentageFormatter,
                                        bottomCalc: () => { return portfolio['metrics']['total_return_percentage'] },
                                        bottomCalcFormatter: percentageFormatter
                                    },
                                ]
                            },
                        ],
                    });
                }

                // Create Tabulator on DOM element with portfolio metrics, if metrics div can be found
                if (document.querySelector('#metrics')) {
                    new Tabulator("#metrics", {
                        maxHeight: "100%",
                        data: [{ ...portfolio['portfolio'], ...portfolio['metrics'] }],
                        layout: "fitDataTable",
                        columns: [
                            {
                                title: "Total investment", field: "total_investment", width: 150,
                                headerHozAlign: "center", hozAlign: "center",
                                formatter: currencyFormatter, formatterParams: { currency: portfolio['portfolio']['currency'] }
                            },
                            {
                                title: "Balance", field: "balance", width: 150,
                                headerHozAlign: "center", hozAlign: "center",
                                formatter: currencyFormatter, formatterParams: { currency: portfolio['portfolio']['currency'] }
                            },
                            {
                                title: "Total cost", headerHozAlign: "center", columns: [
                                    {
                                        field: "total_cost", width: 75, cssClass: "hide-header", hozAlign: "center",
                                        formatter: currencyFormatter, formatterParams: { currency: portfolio['portfolio']['currency'] }
                                    },
                                    {
                                        field: "total_cost_percentage", width: 75, cssClass: "hide-header", hozAlign: "center",
                                        formatter: percentageFormatter, formatterParams: { noColor: true }
                                    },
                                ]
                            },
                            {
                                title: "Total dividend", headerHozAlign: "center", columns: [
                                    {
                                        field: "total_dividend", width: 75, cssClass: "hide-header", hozAlign: "center",
                                        formatter: currencyFormatter, formatterParams: { currency: portfolio['portfolio']['currency'] }
                                    },
                                    {
                                        field: "total_dividend_percentage", width: 75, cssClass: "hide-header", hozAlign: "center",
                                        formatter: percentageFormatter, formatterParams: { noColor: true }
                                    },
                                ]
                            },
                            {
                                title: "Unrealized PnL", headerHozAlign: "center", columns: [
                                    {
                                        field: "unrealized_pnl", width: 75, cssClass: "hide-header", hozAlign: "center",
                                        formatter: pnlFormatter, formatterParams: { currency: portfolio['portfolio']['currency'] }
                                    },
                                    {
                                        field: "unrealized_pnl_percentage", width: 75, cssClass: "hide-header", hozAlign: "center",
                                        formatter: percentageFormatter
                                    },
                                ]
                            },
                            {
                                title: "Realized PnL", headerHozAlign: "center", columns: [
                                    {
                                        field: "realized_pnl", width: 75, cssClass: "hide-header", hozAlign: "center",
                                        formatter: pnlFormatter, formatterParams: { currency: portfolio['portfolio']['currency'] }
                                    },
                                    {
                                        field: "realized_pnl_percentage", width: 75, cssClass: "hide-header", hozAlign: "center",
                                        formatter: percentageFormatter
                                    },
                                ]
                            },
                            {
                                title: "Total return", headerHozAlign: "center", columns: [
                                    {
                                        field: "total_return", width: 75, cssClass: "hide-header", hozAlign: "center",
                                        formatter: pnlFormatter, formatterParams: { currency: portfolio['portfolio']['currency'] }
                                    },
                                    {
                                        field: "total_return_percentage", width: 75, cssClass: "hide-header", hozAlign: "center",
                                        formatter: percentageFormatter
                                    },
                                ]
                            },
                        ],
                    });
                }
            });
    }
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
            if (result.status === 200 || result.status === 201) {
                cell.getRow().update({ watched: !watched });
            }
        });
}