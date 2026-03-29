<?php
/**
 * EchoSmart - PDO Database Singleton
 *
 * @package EchoSmart
 */

require_once __DIR__ . '/config.php';

class Database
{
    private static ?PDO $instance = null;

    private function __construct() {}
    private function __clone() {}

    /**
     * Get the singleton PDO instance.
     */
    public static function getInstance(): PDO
    {
        if (self::$instance === null) {
            $dsn = sprintf(
                'mysql:host=%s;dbname=%s;charset=%s',
                DB_HOST,
                DB_NAME,
                DB_CHARSET
            );

            self::$instance = new PDO($dsn, DB_USER, DB_PASS, [
                PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES   => false,
                PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci",
            ]);
        }

        return self::$instance;
    }

    /**
     * Execute a prepared query and return the statement.
     *
     * @param  string $sql    SQL with named or positional placeholders
     * @param  array  $params Bound parameters
     * @return PDOStatement
     */
    public static function query(string $sql, array $params = []): PDOStatement
    {
        $stmt = self::getInstance()->prepare($sql);
        $stmt->execute($params);
        return $stmt;
    }

    /**
     * Fetch a single row.
     */
    public static function fetchOne(string $sql, array $params = []): ?array
    {
        $row = self::query($sql, $params)->fetch();
        return $row ?: null;
    }

    /**
     * Fetch all rows.
     */
    public static function fetchAll(string $sql, array $params = []): array
    {
        return self::query($sql, $params)->fetchAll();
    }

    /**
     * Validate a table name to prevent injection.
     */
    private static function assertTableName(string $table): void
    {
        if (!preg_match('/^[a-zA-Z_][a-zA-Z0-9_]*$/', $table)) {
            throw new \InvalidArgumentException("Invalid table name: {$table}");
        }
    }

    /**
     * Insert a row and return the last insert ID.
     */
    public static function insert(string $table, array $data): string
    {
        self::assertTableName($table);
        $columns = implode(', ', array_keys($data));
        $placeholders = implode(', ', array_fill(0, count($data), '?'));
        $sql = "INSERT INTO `{$table}` ({$columns}) VALUES ({$placeholders})";
        self::query($sql, array_values($data));
        return self::getInstance()->lastInsertId();
    }

    /**
     * Update rows matching a WHERE clause. Returns affected row count.
     */
    public static function update(string $table, array $data, string $where, array $whereParams = []): int
    {
        self::assertTableName($table);
        $set = implode(', ', array_map(fn($col) => "{$col} = ?", array_keys($data)));
        $sql = "UPDATE `{$table}` SET {$set} WHERE {$where}";
        $stmt = self::query($sql, array_merge(array_values($data), $whereParams));
        return $stmt->rowCount();
    }

    /**
     * Delete rows matching a WHERE clause. Returns affected row count.
     */
    public static function delete(string $table, string $where, array $params = []): int
    {
        self::assertTableName($table);
        $sql = "DELETE FROM `{$table}` WHERE {$where}";
        return self::query($sql, $params)->rowCount();
    }

    /**
     * Begin a transaction.
     */
    public static function beginTransaction(): bool
    {
        return self::getInstance()->beginTransaction();
    }

    /**
     * Commit the current transaction.
     */
    public static function commit(): bool
    {
        return self::getInstance()->commit();
    }

    /**
     * Roll back the current transaction.
     */
    public static function rollBack(): bool
    {
        return self::getInstance()->rollBack();
    }
}
