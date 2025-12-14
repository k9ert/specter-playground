"""Tests for sim_cli.py"""
import base64
import os
import tempfile
from unittest.mock import patch, MagicMock

import sim_cli


class TestGetLabels:
    """Tests for get_labels() function."""

    def test_empty_tree_returns_empty_list(self):
        """Empty tree returns empty labels."""
        with patch.object(sim_cli, 'send') as mock_send:
            mock_send.return_value = {'ok': True, 'tree': {'children': []}}
            labels = sim_cli.get_labels()
            assert labels == []
            mock_send.assert_called_once_with({'action': 'widget_tree'})

    def test_extracts_text_labels_filtering_short(self):
        """Extracts text from nodes with text > 1 char, excludes single char."""
        tree = {
            'ok': True,
            'tree': {
                'text': 'Root',
                'children': [
                    {'text': 'Button One', 'children': []},
                    {'text': 'OK', 'children': []},
                    {'text': 'X', 'children': []},
                ]
            }
        }
        with patch.object(sim_cli, 'send') as mock_send:
            mock_send.return_value = tree
            labels = sim_cli.get_labels()
            assert len(labels) == 3  # Root, Button One, OK
            assert 'Root' in labels
            assert 'Button One' in labels
            assert 'OK' in labels
            assert 'X' not in labels

    def test_traverses_deeply_nested_tree(self):
        """Recursively finds labels in deeply nested structure."""
        tree = {
            'ok': True,
            'tree': {
                'text': 'Level0',
                'children': [{
                    'text': 'Level1',
                    'children': [{
                        'text': 'Level2',
                        'children': [{
                            'text': 'Level3',
                            'children': []
                        }]
                    }]
                }]
            }
        }
        with patch.object(sim_cli, 'send') as mock_send:
            mock_send.return_value = tree
            labels = sim_cli.get_labels()
            assert labels == ['Level0', 'Level1', 'Level2', 'Level3']

    def test_excludes_hash_prefixed_color_codes(self):
        """Labels starting with # are excluded (LVGL color codes)."""
        tree = {
            'ok': True,
            'tree': {
                'text': '#FF0000 Red',
                'children': [
                    {'text': 'Normal', 'children': []},
                    {'text': '#00FF00 Green', 'children': []},
                ]
            }
        }
        with patch.object(sim_cli, 'send') as mock_send:
            mock_send.return_value = tree
            labels = sim_cli.get_labels()
            assert len(labels) == 1
            assert labels == ['Normal']

    def test_returns_empty_on_error_response(self):
        """Returns empty list on error response."""
        with patch.object(sim_cli, 'send') as mock_send:
            mock_send.return_value = {'ok': False, 'error': 'Connection failed'}
            labels = sim_cli.get_labels()
            assert labels == []


class TestSaveScreenshot:
    """Tests for save_screenshot() function."""

    def test_saves_valid_png_with_correct_dimensions(self):
        """Creates valid PNG file with correct dimensions from RGB565 data."""
        # RGB565 red: 0xF800 -> little endian bytes 0x00, 0xF8
        rgb565_data = b'\x00\xF8' * 4  # 4 red pixels for 2x2 image

        with patch.object(sim_cli, 'send') as mock_send:
            mock_send.return_value = {
                'ok': True,
                'width': 2,
                'height': 2,
                'data': base64.b64encode(rgb565_data).decode()
            }

            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                temp_path = f.name

            try:
                result = sim_cli.save_screenshot(temp_path)

                assert result == (2, 2), "Should return (width, height) tuple"
                assert os.path.exists(temp_path), "PNG file should exist"

                # Verify it's a valid PNG with correct properties
                from PIL import Image
                img = Image.open(temp_path)
                assert img.size == (2, 2), "Image dimensions should match"
                assert img.format == 'PNG', "Should be PNG format"

                # Verify pixel color conversion (RGB565 red -> RGB red)
                pixel = img.getpixel((0, 0))
                assert pixel[0] > 200, f"Red channel should be high, got {pixel[0]}"
                assert pixel[1] < 10, f"Green channel should be low, got {pixel[1]}"
                assert pixel[2] < 10, f"Blue channel should be low, got {pixel[2]}"
            finally:
                os.unlink(temp_path)

    def test_returns_none_on_error_without_creating_file(self):
        """Returns None when screenshot fails and doesn't create file."""
        # Use a path that definitely doesn't exist
        temp_path = '/tmp/test_screenshot_should_not_exist_12345.png'
        # Ensure it doesn't exist before test
        if os.path.exists(temp_path):
            os.unlink(temp_path)

        with patch.object(sim_cli, 'send') as mock_send:
            mock_send.return_value = {'ok': False, 'error': 'No display'}
            result = sim_cli.save_screenshot(temp_path)

            assert result is None, "Should return None on error"
            assert not os.path.exists(temp_path), "Should not create file on error"

    def test_reads_raw_data_from_file_path(self):
        """Reads raw RGB565 data from file when 'file' key present."""
        rgb565_data = b'\x00\xF8' * 4  # 4 red pixels

        with tempfile.NamedTemporaryFile(suffix='.raw', delete=False) as raw_file:
            raw_file.write(rgb565_data)
            raw_path = raw_file.name

        with patch.object(sim_cli, 'send') as mock_send:
            mock_send.return_value = {
                'ok': True,
                'width': 2,
                'height': 2,
                'file': raw_path
            }

            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                temp_path = f.name

            try:
                result = sim_cli.save_screenshot(temp_path)
                assert result == (2, 2)
                assert os.path.exists(temp_path)
            finally:
                os.unlink(temp_path)
                os.unlink(raw_path)


class TestSend:
    """Tests for send() function."""

    def test_sends_json_command_and_parses_response(self):
        """Sends JSON command over socket and parses JSON response."""
        mock_socket = MagicMock()
        mock_socket.recv.return_value = b'{"ok": true, "pong": true}\n'

        with patch('socket.socket', return_value=mock_socket):
            result = sim_cli.send({'action': 'ping'})

        assert result == {'ok': True, 'pong': True}
        mock_socket.connect.assert_called_once_with(('127.0.0.1', 9876))
        mock_socket.settimeout.assert_called_once_with(2)
        mock_socket.sendall.assert_called_once()
        mock_socket.close.assert_called_once()

        # Verify sent data is valid JSON with newline
        sent_data = mock_socket.sendall.call_args[0][0]
        assert sent_data.endswith(b'\n'), "Should end with newline"
        assert b'"action"' in sent_data
        assert b'"ping"' in sent_data


class TestGetState:
    """Tests for get_state() function."""

    def test_calls_get_state_action(self):
        """Sends get_state action and returns response."""
        expected = {'ok': True, 'ui': {'current_menu_id': 'main'}, 'specter': {}}
        with patch.object(sim_cli, 'send') as mock_send:
            mock_send.return_value = expected
            result = sim_cli.get_state()

            assert result == expected
            mock_send.assert_called_once_with({'action': 'get_state'})


class TestNavigate:
    """Tests for navigate() function."""

    def test_navigate_to_menu(self):
        """Sends navigate action with target menu."""
        with patch.object(sim_cli, 'send') as mock_send:
            mock_send.return_value = {'ok': True, 'navigated': 'settings'}
            result = sim_cli.navigate('settings')

            mock_send.assert_called_once_with({'action': 'navigate', 'target': 'settings'})
            assert result['navigated'] == 'settings'

    def test_navigate_back(self):
        """Sends navigate action with back target."""
        with patch.object(sim_cli, 'send') as mock_send:
            mock_send.return_value = {'ok': True, 'navigated': 'back'}
            result = sim_cli.navigate('back')

            mock_send.assert_called_once_with({'action': 'navigate', 'target': 'back'})
            assert result['navigated'] == 'back'
