'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, HelpCircle } from 'lucide-react';

type Question =
  | { id: string; type: 'single'; prompt: string; options: string[]; answer: number }
  | { id: string; type: 'true_false'; prompt: string; answer: boolean };

export interface QuizContent {
  questions: Question[];
}

export interface QuizBlockProps {
  title: string;
  instructions?: string;
  content: QuizContent;
  hints?: string[];
  onComplete?: (score: number, total: number) => void;
}

export default function QuizBlock({ title, instructions, content, hints = [], onComplete }: QuizBlockProps) {
  const [answers, setAnswers] = useState<Record<string, number | boolean>>({});
  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState(0);

  const submit = () => {
    let s = 0;
    for (const q of content.questions) {
      const a = answers[q.id];
      if (q.type === 'single' && typeof a === 'number' && a === q.answer) s += 1;
      if (q.type === 'true_false' && typeof a === 'boolean' && a === q.answer) s += 1;
    }
    setScore(s);
    setSubmitted(true);
    onComplete?.(s, content.questions.length);
  };

  return (
    <Card className="border border-blue-200">
      <CardHeader>
        <CardTitle className="text-xl">{title}</CardTitle>
        {instructions && <p className="text-gray-600 text-sm">{instructions}</p>}
      </CardHeader>
      <CardContent className="space-y-5">
        {content.questions.map((q, idx) => (
          <div key={q.id} className="space-y-2">
            <div className="flex items-center gap-2">
              <Badge variant="outline">Q{idx + 1}</Badge>
              <p className="font-medium">{q.prompt}</p>
              {submitted && (
                <span className="ml-2">
                  {(() => {
                    const a = answers[q.id];
                    const correct = q.type === 'single' ? a === q.answer : a === q.answer;
                    return correct ? (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    ) : (
                      <XCircle className="h-4 w-4 text-red-600" />
                    );
                  })()}
                </span>
              )}
            </div>
            {q.type === 'single' && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {q.options.map((opt, i) => (
                  <label key={i} className={`flex items-center gap-2 p-2 rounded border ${answers[q.id] === i ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}>
                    <input
                      type="radio"
                      name={q.id}
                      checked={answers[q.id] === i}
                      onChange={() => setAnswers({ ...answers, [q.id]: i })}
                    />
                    <span>{opt}</span>
                  </label>
                ))}
              </div>
            )}
            {q.type === 'true_false' && (
              <div className="flex gap-2">
                {[
                  { label: 'True', val: true },
                  { label: 'False', val: false },
                ].map((o) => (
                  <Button
                    key={String(o.val)}
                    type="button"
                    variant={answers[q.id] === o.val ? 'default' : 'outline'}
                    onClick={() => setAnswers({ ...answers, [q.id]: o.val })}
                  >
                    {o.label}
                  </Button>
                ))}
              </div>
            )}
          </div>
        ))}

        {hints.length > 0 && !submitted && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <HelpCircle className="h-4 w-4" />
            <span>Hints: {hints.join(' • ')}</span>
          </div>
        )}

        <div className="flex items-center justify-between pt-2">
          {submitted ? (
            <div className="text-sm font-medium">
              Score: {score} / {content.questions.length}
            </div>
          ) : (
            <div />
          )}
          <Button type="button" onClick={submit} disabled={submitted}>
            {submitted ? 'Submitted' : 'Submit Answers'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
