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

    // Also call currencyFormatter to format number and add currency
    return currencyFormatter(cell, formatterParams, onRendered);
}


export { currencyFormatter, pnlFormatter };