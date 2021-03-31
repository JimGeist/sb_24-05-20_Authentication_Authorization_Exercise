// Cupcakes

const ROOT_APP = "http://127.0.0.1:5000";
const ROOT_API = `${ROOT_APP}/api/cupcakes`;

async function get_cupcakes() {

    /** function synopsis:
     *   function calls the server to get all cupcakes.
     * 
     *   Server will reply with a JSON response which contains data
     *   
     *   ROOT_API = http://127.0.0.1/api/cupcakes
     *    get all cupcakes: get call to the root api.
     * 
     *   {
     *      statusIsOK: true when OK, false when status was not 200
     *      results: object cupcakes with an array of cupcake objects.
     *      message: the error message
     *   }
     */

    results_out = {
        "statusIsOK": null,
        "results": null,
        "message": null
    }

    try {
        const res = await axios.get(`${ROOT_API}`);

        if (res.status === 200) {
            results_out["statusIsOK"] = true;
            results_out["results"] = res.data;
        } else {
            results_out["statusIsOK"] = false;
            results_out["message"] = `Status was not 200 (OK). response code = ${res.status}. `;
        }

    } catch (e) {
        results_out["statusIsOK"] = false;
        results_out["message"] = `An unexpected error (${e.message}) occurred while connecting to server. `;
    }

    return results_out;

}

function build_cupcake_display($formElement, cupcake) {

    const $newDiv = $('<div>').addClass('cupcake');

    $('<img>').attr('src', cupcake.image).attr('alt', "no cupcake image").appendTo($newDiv);
    $('<span>').text(`${cupcake.flavor}  ${cupcake.size}  ${cupcake.rating}`).appendTo($newDiv);
    $formElement.append($newDiv);

}


async function build_cupcake_list() {

    // 
    cupcake_info = await get_cupcakes()
    if (cupcake_info.statusIsOK) {
        if (cupcake_info.results.cupcakes.length > 0) {

            for (let cupcake of cupcake_info.results.cupcakes) {
                // do this for each element in array
                build_cupcake_display($('td'), cupcake)
            }

        }

    } else {
        $('#messages').text(cupcake_info.message)
    }

}


async function handleAdd(event) {

    event.preventDefault();

    let flavor = $("#form-flavor").val().trim();
    let size = $("#form-size").val().trim();
    let rating = $("#form-rating").val();
    let image = $("#form-image").val().trim();

    $('#messages').html('&nbsp;')

    try {
        const res = await axios.post(`${ROOT_API}`, {
            flavor,
            rating,
            size,
            image
        },
            {
                validateStatus: function (status) {
                    // Resolve when the status code is less than 500
                    return status < 500;
                }
            }
        );

        if (res.status === 201) {
            build_cupcake_display($('td'), res.data.cupcake);

            $('input').val('');

        } else {
            $('#messages').text(res.data.error)
        }

    } catch (e) {
        $('#messages').text(`An unexpected error (${e.message}) occurred. `)
    }

}


$(function () {

    /* When DOM loads, 
        call to get the cupcakes via api
        add event listener for Add Cupcake button click.
    */

    //alert("JavaScript loaded");

    // build the table to hold the div for each cupcake. div of divs just
    //  does not seem to work for me because everything after the div is 
    //  still floats after the div instead of being below all the divs.

    $('<table>').appendTo('#contents')
    $('<tbody>').appendTo('table')
    $('<tr>').appendTo('tbody')
    $('<td>').appendTo('tr')
    build_cupcake_list();

    // listener for click of the submit form button
    $("#add-cupcake").on("click", handleAdd);

});