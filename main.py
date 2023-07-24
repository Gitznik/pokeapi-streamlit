import streamlit as st

from pokeapi import PokeApiConnection

st.header("Interactive PokeAPI Explorer")
st.divider()

conn = PokeApiConnection("PokeAPI")
res_endpoints = conn.list_available_endpoints()
endpoint = st.selectbox("Choose endpoint", options=res_endpoints.index)


def map_name_or_id(choice: str, options: list[str]) -> str | int | None:
    if choice == "name":
        return st.selectbox(
            "Please select a name to explore in this endpoint", options=options
        )
    if choice == "id":
        return int(
            st.number_input(
                "Please select an ID to explore in this endpoint",
                step=1,
                min_value=1,
                max_value=len(options),
            )
        )


if endpoint:
    res_resources = conn.list_available_resources(endpoint, limit=1000)
    st.write("These are the available resources in this endpoint:")
    st.dataframe(res_resources, hide_index=True)
    st.divider()

    id_or_name = st.radio(
        "Do you want to explore the resources by name or id?",
        ["name", "id"],
        horizontal=True,
    )
    if id_or_name:
        selection = map_name_or_id(id_or_name, res_resources.name.tolist())
        if selection:
            res_resource = conn.get_resource(endpoint, selection)
            st.json(res_resource, expanded=False)
        else:
            st.write("Please select a name or ID to explore")
else:
    st.write("Please select an endpoint to start exploring")
