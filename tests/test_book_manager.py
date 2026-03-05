#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 BookManager 模块
"""

import sys
import os
import tempfile
import unittest
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from book_manager import BookManager, Book


class TestBook(unittest.TestCase):
    """测试 Book 类"""

    def test_book_creation(self):
        """测试创建书籍"""
        book = Book(title="测试书籍", author="测试作者", isbn="1234567890")
        self.assertEqual(book.title, "测试书籍")
        self.assertEqual(book.author, "测试作者")
        self.assertEqual(book.isbn, "1234567890")
        self.assertFalse(book.available)
        self.assertEqual(book.locations, [])
        self.assertFalse(book.monitor)

    def test_book_to_dict(self):
        """测试书籍转换为字典"""
        book = Book(title="测试书籍", author="测试作者")
        book.available = True
        book.locations = ["位置1", "位置2"]
        book.monitor = True

        book_dict = book.to_dict()
        self.assertEqual(book_dict["title"], "测试书籍")
        self.assertEqual(book_dict["available"], True)
        self.assertEqual(book_dict["locations"], ["位置1", "位置2"])
        self.assertEqual(book_dict["monitor"], True)

    def test_book_from_dict(self):
        """测试从字典创建书籍"""
        data = {
            "book_id": "test123",
            "title": "测试书籍",
            "author": "测试作者",
            "isbn": "123456",
            "available": True,
            "locations": ["位置1"],
            "monitor": True,
        }

        book = Book.from_dict(data)
        self.assertEqual(book.book_id, "test123")
        self.assertEqual(book.title, "测试书籍")
        self.assertEqual(book.available, True)
        self.assertEqual(book.monitor, True)


class TestBookManager(unittest.TestCase):
    """测试 BookManager 类"""

    def setUp(self):
        """测试前创建临时文件"""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        self.temp_file.write('{"books": []}')
        self.temp_file.close()
        self.manager = BookManager(self.temp_file.name)

    def tearDown(self):
        """测试后删除临时文件"""
        os.unlink(self.temp_file.name)

    def test_add_book(self):
        """测试添加书籍"""
        book = Book(title="测试书籍", author="测试作者")
        book_id, is_new = self.manager.add_book(book)

        self.assertIsNotNone(book_id)
        self.assertTrue(is_new)
        self.assertEqual(len(self.manager.get_all_books()), 1)

    def test_remove_book(self):
        """测试删除书籍"""
        book = Book(title="测试书籍")
        book_id, _ = self.manager.add_book(book)

        self.assertTrue(self.manager.remove_book(book_id))
        self.assertEqual(len(self.manager.get_all_books()), 0)

    def test_get_book(self):
        """测试获取书籍"""
        book = Book(title="测试书籍", author="测试作者")
        book_id, _ = self.manager.add_book(book)

        retrieved_book = self.manager.get_book(book_id)
        self.assertIsNotNone(retrieved_book)
        self.assertEqual(retrieved_book.title, "测试书籍")

    def test_toggle_monitor(self):
        """测试切换监控状态"""
        book = Book(title="测试书籍")
        book_id, _ = self.manager.add_book(book)

        # 初始状态应该是关闭
        book = self.manager.get_book(book_id)
        self.assertFalse(book.monitor)

        # 切换为开启
        status = self.manager.toggle_monitor(book_id)
        self.assertTrue(status)

        # 再次切换为关闭
        status = self.manager.toggle_monitor(book_id)
        self.assertFalse(status)

    def test_get_monitoring_books(self):
        """测试获取正在监控的书籍"""
        book1 = Book(title="书籍1")
        book2 = Book(title="书籍2")
        book2.monitor = True

        self.manager.add_book(book1)
        self.manager.add_book(book2)

        monitoring = self.manager.get_monitoring_books()
        self.assertEqual(len(monitoring), 1)
        self.assertEqual(monitoring[0].title, "书籍2")

    def test_add_duplicate_book_by_isbn(self):
        """测试通过ISBN添加重复书籍应该更新而不是新增"""
        book1 = Book(title="书籍1", isbn="1234567890")
        book_id1, is_new1 = self.manager.add_book(book1)
        self.assertTrue(is_new1)

        # 添加相同ISBN的书籍
        book2 = Book(title="书籍1（更新）", isbn="1234567890", author="作者")
        book_id2, is_new2 = self.manager.add_book(book2)

        # 应该返回相同的book_id，且不是新的
        self.assertEqual(book_id1, book_id2)
        self.assertFalse(is_new2)
        # 应该只有1本书
        self.assertEqual(len(self.manager.get_all_books()), 1)
        # 书籍信息应该被更新
        updated_book = self.manager.get_book(book_id1)
        self.assertEqual(updated_book.title, "书籍1（更新）")
        self.assertEqual(updated_book.author, "作者")

    def test_add_duplicate_book_by_title(self):
        """测试通过标题添加重复书籍应该更新而不是新增"""
        book1 = Book(title="书籍2", author="作者2")
        book_id1, is_new1 = self.manager.add_book(book1)
        self.assertTrue(is_new1)

        # 添加相同标题的书籍
        book2 = Book(title="书籍2", author="作者2", isbn="0987654321")
        book_id2, is_new2 = self.manager.add_book(book2)

        # 应该返回相同的book_id，且不是新的
        self.assertEqual(book_id1, book_id2)
        self.assertFalse(is_new2)
        # 应该只有1本书
        self.assertEqual(len(self.manager.get_all_books()), 1)


if __name__ == "__main__":
    unittest.main()
