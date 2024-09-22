import os
import logging
from typing import Dict, List

import asyncio
import streamlit as st

from library_name_generator import LibraryName, generate_library_name
from result_saver import ResultSaver
from models import LibraryName, ResultItem

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AppState:
    def __init__(self):
        if 'app_state' not in st.session_state:
            st.session_state.app_state = {
                'results': [],
                'history': [],
                'view_history': False,
                'view_starred': False,
                'star_states': {}
            }
        self.state = st.session_state.app_state

    def get(self, key):
        return self.state.get(key)

    def set(self, key, value):
        self.state[key] = value
        st.session_state.app_state = self.state

def maintain_scroll_position():
    st.markdown(
        """
        <script>
        var scrollPosition = window.pageYOffset;
        window.addEventListener('load', function() {
            window.scrollTo(0, scrollPosition);
        });
        </script>
        """,
        unsafe_allow_html=True
    )

def render_input_form():
    language: str = st.text_input("Programming Language:")
    topic: str = st.text_input("Library Topic:")
    purpose: str = st.text_input("Library Purpose:")
    number_of_names: int = st.slider("Number of names to generate:", 1, 10, 5)
    return language, topic, purpose, number_of_names

async def generate_names_async(language: str, topic: str, purpose: str, number_of_names: int):
    inputs: Dict[str, str | int] = {
        'language': language,
        'topic': topic,
        'purpose': purpose,
        'number_of_names': number_of_names
    }
    results: List[LibraryName] = await generate_library_name(inputs)
    results = results[:number_of_names]
    return [ResultItem(name=result.name, explanation=result.explanation, starred=False) for result in results]

def render_item(item: ResultItem, index: int, is_history: bool, result_saver: ResultSaver, app_state: AppState):
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        st.write(f"- {item.name}: {item.explanation}")
    with col2:
        render_star_button(item, index, is_history, result_saver, app_state)
    with col3:
        render_delete_button(item, index, is_history, result_saver, app_state)
    with col4:
        st.write("⭐" if app_state.get('star_states').get(f"star_{index}", False) else "")

def render_star_button(item: ResultItem, index: int, is_history: bool, result_saver: ResultSaver, app_state: AppState):
    key = f"star_{index}"
    if key not in app_state.get('star_states'):
        app_state.get('star_states')[key] = item.starred

    if st.button("Star" if not app_state.get('star_states')[key] else "Unstar", key=f"star_button_{index}"):
        app_state.get('star_states')[key] = not app_state.get('star_states')[key]
        item.starred = app_state.get('star_states')[key]
        if is_history:
            result_saver.save_results(app_state.get('history'))
        st.rerun()

def render_delete_button(item: ResultItem, index: int, is_history: bool, result_saver: ResultSaver, app_state: AppState):
    if st.button("Delete", key=f"delete_{index}"):
        if is_history:
            app_state.get('history').pop(index)
            result_saver.save_results(app_state.get('history'))
        else:
            app_state.get('results').pop(index)
        st.rerun()

def render_save_button(result_saver: ResultSaver, default_path: str, app_state: AppState):
    if st.button("Save Results"):
        try:
            logger.debug(f"Attempting to save results to: {default_path}")
            existing_names = set(item.name for item in app_state.get('history'))
            unique_new_results = [item for item in app_state.get('results') if item.name not in existing_names]
            app_state.get('history').extend(unique_new_results)
            result_saver.save_results(app_state.get('history'))
            st.success(f"Results saved to {default_path}")
            logger.debug(f"Results successfully saved to: {default_path}")
            app_state.set('results', [])
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}", exc_info=True)
            st.error(f"Error saving results: {str(e)}")

def main() -> None:
    st.title("Library Name Generator")
    st.write("This app generates library names based on the provided language, topic, and purpose.")
    app_state = AppState()

    current_dir = os.getcwd()
    default_path = os.path.join(current_dir, "history", "results.json")
    result_saver = ResultSaver(default_path)

    if not app_state.get('history'):
        app_state.set('history', result_saver.load_results())

    # Input form
    language, topic, purpose, number_of_names = render_input_form()

    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        generate_button = st.button("Generate Names")
    with col2:
        history_button = st.button("View History")
    with col3:
        starred_button = st.button("View Starred")

    # Main content container
    main_container = st.container()

    with main_container:
        if generate_button:
            with st.spinner("Generating names..."):
                results = asyncio.run(generate_names_async(language, topic, purpose, number_of_names))
                app_state.set('results', results)
                app_state.set('view_history', False)
                app_state.set('view_starred', False)
                st.rerun()

        if history_button:
            app_state.set('view_history', True)
            app_state.set('view_starred', False)
            st.rerun()

        if starred_button:
            app_state.set('view_starred', True)
            app_state.set('view_history', False)
            st.rerun()

        if app_state.get('view_history') or app_state.get('view_starred'):
            display_items = app_state.get('history')
            if app_state.get('view_starred'):
                display_items = [item for item in display_items if item.starred]
                st.write("Starred Items:")
            else:
                st.write("History:")
            for i, item in enumerate(display_items):
                render_item(item, i, True, result_saver, app_state)
        elif app_state.get('results'):
            st.write("Results generated successfully!")
            for i, item in enumerate(app_state.get('results')):
                render_item(item, i, False, result_saver, app_state)
            render_save_button(result_saver, default_path, app_state)

    # Maintain scroll position
    maintain_scroll_position()

if __name__ == "__main__":
    main()